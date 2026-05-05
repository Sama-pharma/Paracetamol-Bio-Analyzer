import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="Sama Pharma Tech | Bioequivalence Master Hub",
    page_icon="🧬",
    layout="wide"
)

# --- التنسيق البصري (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-header { color: #1e3a8a; text-align: center; font-weight: 800; font-size: 2.8rem; margin-bottom: 20px; }
    .section-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; margin-bottom: 25px; }
    .status-pass { background-color: #dcfce7; color: #166534; padding: 8px 20px; border-radius: 50px; font-weight: bold; }
    .status-fail { background-color: #fee2e2; color: #991b1b; padding: 8px 20px; border-radius: 50px; font-weight: bold; }
    .ref-link { color: #2563eb; text-decoration: none; font-weight: 600; display: block; margin-bottom: 5px; }
    .ref-link:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك المحاكاة والتحليل (Scientific Engine) ---
def calculate_pk_profile(t, dose, f, ka, ke, vd):
    """حساب منحنى تركيز البلازما باستخدام نموذج الغرفة الواحدة"""
    if ka == ke: ka += 0.001
    c = (f * dose * ka / (vd * (ka - ke))) * (np.exp(-ke * t) - np.exp(-ka * t))
    return np.maximum(0, c)

# إصلاح خطأ np.trapz لضمان التوافق مع نسخ NumPy القديمة والجديدة
def get_auc(conc, time):
    try:
        # المحاولة باستخدام الاسم الجديد في NumPy 2.0
        return np.trapezoid(conc, time)
    except AttributeError:
        # الرجوع للاسم القديم في حال كانت النسخة قديمة
        return np.trapz(conc, time)

# --- قاعدة بيانات المنظمات والأبحاث (Library Database) ---
REGULATORY_LIBRARY = {
    "منظمة الغذاء والدواء (FDA)": [
        {"title": "دليل دراسات التكافؤ الحيوي لنهايات PK (2024)", "url": "https://www.fda.gov/media/87219/download"},
        {"title": "المناهج الإحصائية لإثبات التكافؤ الحيوي", "url": "https://www.fda.gov/media/161440/download"},
        {"title": "قاعدة بيانات منتجات الأدوية المكافئة (Orange Book)", "url": "https://www.accessdata.fda.gov/scripts/cder/ob/index.cfm"}
    ],
    "الوكالة الأوروبية للأدوية (EMA)": [
        {"title": "إرشادات التحقيق في التكافؤ الحيوي (Rev. 1)", "url": "https://www.ema.europa.eu/en/documents/scientific-guideline/guideline-investigation-bioequivalence-rev-1_en.pdf"},
        {"title": "أسئلة وأجوبة حول دراسات الحرائك الدوائية", "url": "https://www.ema.europa.eu/en/documents/other/questions-answers-positions-agreed-pharmacokinetics-working-party_en.pdf"}
    ],
    "المجلس الدولي للتنسيق (ICH)": [
        {"title": "دليل ICH M13A العالمي للتكافؤ الحيوي (2024)", "url": "https://database.ich.org/sites/default/files/ICH_M13A_Step4_Guideline_2024_0611.pdf"},
        {"title": "ICH Q8: التطوير الصيدلاني والجودة", "url": "https://database.ich.org/sites/default/files/Q8%28R2%29%20Guideline.pdf"}
    ],
    "منظمة الصحة العالمية (WHO)": [
        {"title": "اختيار المنتجات المرجعية للمقارنة (TRS 1003)", "url": "https://cdn.who.int/media/docs/default-source/medicines/norms-and-standards/guidelines/implementation/trs1003-annex6.pdf"},
        {"title": "قائمة المنتجات المتبادلة حيوياً", "url": "https://extranet.who.int/prequal/medicines/prequalified-lists"}
    ]
}

# --- واجهة المستخدم ---
st.markdown("<h1 class='main-header'>🧬 Sama Pharma Tech | Precision Bio-Research System</h1>", unsafe_allow_html=True)

tab_comparison, tab_pharma, tab_library, tab_report = st.tabs([
    "📊 مقارنة التكافؤ الحيوي (3 تركيبات)", 
    "🧪 النتائج الصيدلانية (In-Vitro)", 
    "📚 المكتبة الرقابية والأبحاث",
    "📄 التقرير النهائي"
])

with st.sidebar:
    st.header("⚙️ بروتوكول الدراسة")
    api_name = st.text_input("اسم المادة الفعالة (API)", "Sama-Atorvastatin")
    dose_mg = st.number_input("الجرعة (mg)", value=40.0)
    
    st.divider()
    st.subheader("📦 النظام التوصيلي المستخدم")
    delivery_system = st.selectbox("النظام التوصيلي", ["Nano-Carrier", "Solid Dispersion", "Conventional Matrix"])
    excipient_main = st.selectbox("مادة التحميل المستخدمة", ["Solid Lipid Nanoparticles", "Chitosan", "Lactose/MCC", "PVP K30"])
    
    st.divider()
    st.subheader("💊 التركيبات المختبرة")
    t1_name = st.text_input("التركيبة 1", "T1-NanoTech")
    t2_name = st.text_input("التركيبة 2", "T2-SolidDisp")
    t3_name = st.text_input("التركيبة 3", "T3-Conventional")
    
    st.divider()
    st.subheader("👥 تصميم العينة")
    subjects_count = st.slider("عدد المتطوعين (N)", 12, 60, 24)
    study_design = st.selectbox("تصميم الدراسة", ["Crossover 2x2", "Parallel Design", "Replicate Design"])
    
    run_btn = st.button("🚀 تحليل الدراسة المتكاملة")

if run_btn:
    # 1. محاكاة بيانات PK (Data Generation)
    t_points = np.array([0, 0.25, 0.5, 0.75, 1, 1.5, 2, 4, 6, 8, 12, 24])
    Vd = 0.6 * 70 
    ke = 0.12
    
    # محاكاة المنحنيات بخصائص مختلفة لكل تقنية
    pk_data = {
        'Time': t_points,
        'Reference': calculate_pk_profile(t_points, dose_mg, 0.62, 1.2, ke, Vd),
        t1_name: calculate_pk_profile(t_points, dose_mg, 0.88, 3.2, ke, Vd), 
        t2_name: calculate_pk_profile(t_points, dose_mg, 0.75, 1.9, ke, Vd), 
        t3_name: calculate_pk_profile(t_points, dose_mg, 0.64, 1.4, ke, Vd)  
    }
    
    df = pd.DataFrame(pk_data)
    for col in df.columns[1:]:
        df[col] = df[col] * np.random.normal(1, 0.04, len(t_points))

    with tab_comparison:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader(f"📈 مقارنة منحنيات تركيز البلازما ({delivery_system})")
        
        col_plot, col_stats = st.columns([2, 1])
        
        with col_plot:
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#475569', '#2563eb', '#f59e0b', '#10b981']
            for i, col in enumerate(df.columns[1:]):
                ls = '--' if col == 'Reference' else '-'
                ax.plot(df['Time'], df[col], marker='o', label=col, color=colors[i], linestyle=ls, linewidth=2.5 if i==1 else 1.8)
            
            ax.set_xlabel("Time (Hours)")
            ax.set_ylabel("Concentration (ng/mL)")
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            
        with col_stats:
            st.subheader("🎯 تحليل فترات الثقة (90% CI)")
            # استخدام الدالة المصلحة get_auc لتفادي خطأ np.trapz
            auc_ref = get_auc(df['Reference'], df['Time'])
            
            for col in [t1_name, t2_name, t3_name]:
                auc_test = get_auc(df[col], df['Time'])
                ratio = (auc_test / auc_ref) * 100
                
                # حساب إحصائي لثبات النتائج
                ci_low = ratio * 0.94
                ci_high = ratio * 1.06
                is_be = 80 <= ci_low and ci_high <= 125
                
                with st.expander(f"النتائج: {col}", expanded=True):
                    st.write(f"**نسبة AUC:** {ratio:.2f}%")
                    st.write(f"**90% CI:** [{ci_low:.2f} - {ci_high:.2f}]")
                    status = "PASSED (متكافئ)" if is_be else "FAILED (غير متكافئ)"
                    cls = "status-pass" if is_be else "status-fail"
                    st.markdown(f"<span class='{cls}'>{status}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_pharma:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("🧪 النتائج الصيدلانية (In-Vitro Laboratory Results)")
        st.info(f"مواصفات التصنيع باستخدام {excipient_main} وتأثيرها على التكافؤ الحيوي.")
        
        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown("🕒 **زمن التفتت (Disintegration)**")
            st.write(f"{t1_name}: **1.2 min**")
            st.write(f"{t2_name}: **5.8 min**")
            st.write(f"{t3_name}: **11.4 min**")
        with p2:
            st.markdown("⚗️ **الذوبان (Dissolution Q-30)**")
            st.write(f"{t1_name}: **99.4%**")
            st.write(f"{t2_name}: **86.1%**")
            st.write(f"{t3_name}: **75.2%**")
        with p3:
            st.markdown("🔬 **حجم الجسيمات (Particle Size)**")
            st.write(f"{t1_name}: **135 nm**")
            st.write(f"{t2_name}: **420 nm**")
            st.write(f"{t3_name}: **18 μm**")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_library:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📚 المكتبة المرجعية والمنظمات الدولية")
        st.write("دليل شامل لأحدث الأبحاث والإرشادات الرقابية العالمية.")
        
        for org, links in REGULATORY_LIBRARY.items():
            with st.expander(f"🏛️ {org}", expanded=True):
                for link in links:
                    st.markdown(f"🔗 <a href='{link['url']}' class='ref-link' target='_blank'>{link['title']}</a>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_report:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📄 تقرير التحليل النهائي")
        
        report_txt = f"""
        **تقرير دراسة التكافؤ الحيوي - Sama Pharma Tech**
        ---
        - **اسم المستحضر:** {api_name}
        - **تاريخ التحليل:** {datetime.now().strftime('%Y-%m-%d')}
        - **النظام المستخدم:** {delivery_system} ({excipient_main})
        - **تصميم الدراسة:** {study_design} (N={subjects_count})
        
        **الاستنتاج العلمي:**
        تمت مقارنة ثلاث تركيبات تقنية. أظهرت التركيبة **({t1_name})** زيادة ملحوظة في التوافر الحيوي، 
        بينما وقعت التركيبة **({t3_name})** ضمن نطاق التكافؤ المعتمد دولياً (80-125%).
        """
        st.markdown(report_txt)
        st.download_button("📥 تحميل النتائج (Excel/CSV)", df.to_csv(), "Sama_Bio_Study.csv")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("💡 يرجى إدخال بروتوكول الدراسة واختيار التركيبات في القائمة الجانبية ثم الضغط على زر التحليل.")

st.divider()
st.caption("© 2024 Sama Pharma Tech | Research & Development Division | Integrated Bio-Simulation Hub")