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
    .status-pass { background-color: #dcfce7; color: #166534; padding: 8px 20px; border-radius: 50px; font-weight: bold; display: inline-block; }
    .status-fail { background-color: #fee2e2; color: #991b1b; padding: 8px 20px; border-radius: 50px; font-weight: bold; display: inline-block; }
    .ref-link { color: #2563eb; text-decoration: none; font-weight: 600; display: block; margin-bottom: 8px; border-left: 3px solid #2563eb; padding-left: 10px; }
    .ref-link:hover { background-color: #f1f5f9; }
    .metric-label { color: #64748b; font-size: 0.9rem; font-weight: bold; }
    .metric-value { color: #1e293b; font-size: 1.2rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك المحاكاة والتحليل (Scientific Engine) ---
def calculate_pk_profile(t, dose, f, ka, ke, vd):
    """حساب منحنى تركيز البلازما باستخدام نموذج الغرفة الواحدة"""
    if ka == ke: ka += 0.001
    c = (f * dose * ka / (vd * (ka - ke))) * (np.exp(-ke * t) - np.exp(-ka * t))
    return np.maximum(0, c)

def get_auc(conc, time):
    """حساب المساحة تحت المنحنى مع مراعاة إصدارات NumPy"""
    try:
        return np.trapezoid(conc, time)
    except AttributeError:
        return np.trapz(conc, time)

# --- قاعدة بيانات المواد المضافة والأشكال الصيدلانية ---
EXCIPIENTS_DB = {
    "الصور التقليدية (Solid/Liquid)": [
        "Lactose Monohydrate", "Microcrystalline Cellulose (MCC)", "Magnesium Stearate", 
        "PVP K30", "Crospovidone", "HPMC", "Starch", "Sodium Lauryl Sulfate"
    ],
    "الصور النانوية (Nano-Systems)": [
        "Chitosan Nanoparticles", "Solid Lipid Nanoparticles (SLN)", "PLGA Polymers", 
        "Gold Nanoparticles", "Liposomes (Phospholipids)", "PEGylated Lipids", "Mesoporous Silica"
    ]
}

# --- قاعدة بيانات المنظمات والأبحاث الشاملة ---
REGULATORY_LIBRARY = {
    "الهيئات الرقابية الدولية (Regulatory Agencies)": [
        {"title": "FDA: Bioequivalence Studies for PK Endpoints (2024)", "url": "https://www.fda.gov/media/87219/download"},
        {"title": "EMA: Guideline on Investigation of Bioequivalence", "url": "https://www.ema.europa.eu/en/documents/scientific-guideline/guideline-investigation-bioequivalence-rev-1_en.pdf"},
        {"title": "ICH M13A: Global Bioequivalence Standards", "url": "https://database.ich.org/sites/default/files/ICH_M13A_Step4_Guideline_2024_0611.pdf"},
        {"title": "WHO: TRS 1003 - Interchangeable Medicines", "url": "https://cdn.who.int/media/docs/default-source/medicines/norms-and-standards/guidelines/implementation/trs1003-annex6.pdf"}
    ],
    "المكتبات البحثية والأبحاث المتقدمة": [
        {"title": "PubMed: Advances in Bioavailability of Nano-drugs", "url": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"title": "ScienceDirect: Pharmaceutical Carriers and PK Profiles", "url": "https://www.sciencedirect.com/"},
        {"title": "Google Scholar: Recent Bioequivalence Research (2025)", "url": "https://scholar.google.com/"}
    ]
}

# --- واجهة المستخدم الرئيسية ---
st.markdown("<h1 class='main-header'>🧬 Sama Pharma Tech | Precision Bio-Research Hub</h1>", unsafe_allow_html=True)

tab_comparison, tab_pharma, tab_library, tab_report = st.tabs([
    "📊 مقارنة التكافؤ الحيوي و In-Vivo", 
    "🧪 الأشكال الصيدلانية والمواد المضافة", 
    "📚 المكتبة والمراجع والمنظمات",
    "📄 تقرير الدراسة النهائي"
])

with st.sidebar:
    st.header("⚙️ بروتوكول الدراسة")
    api_name = st.text_input("اسم المادة الفعالة (API)", "Sama-Paracetamol")
    dose_mg = st.number_input("الجرعة (mg)", value=500.0)
    
    st.divider()
    st.subheader("📦 اختيار الشكل والمواد المضافة")
    form_type = st.radio("نوع الصورة الصيدلانية", ["الصور التقليدية (Solid/Liquid)", "الصور النانوية (Nano-Systems)"])
    selected_excipients = st.multiselect("المواد المضافة المستخدمة", EXCIPIENTS_DB[form_type])
    
    if form_type == "الصور النانوية (Nano-Systems)":
        particle_size = st.number_input("حجم الجسيمات (nm)", value=150, help="إدخال حجم الجسيمات لتقييم التأثير على الامتصاص")
    
    st.divider()
    st.subheader("💊 التركيبات المختبرة")
    t1_name = st.text_input("التركيبة 1", "Nano-F1")
    t2_name = st.text_input("التركيبة 2", "Micro-F2")
    t3_name = st.text_input("التركيبة 3", "Conv-F3")
    
    st.divider()
    st.subheader("👥 معايير إحصائية")
    subjects = st.slider("عدد المتطوعين (N)", 12, 60, 24)
    
    run_btn = st.button("🚀 تشغيل التحليل المتكامل")

if run_btn:
    # 1. توليد البيانات (PK Simulation)
    t_points = np.array([0, 0.25, 0.5, 0.75, 1, 1.5, 2, 4, 6, 8, 12, 24])
    Vd = 0.7 * 70
    ke = 0.15
    
    # محاكاة تعتمد على نوع الشكل وحجم الجسيمات
    ka_nano = 4.0 if form_type == "الصور النانوية (Nano-Systems)" else 1.8
    f_nano = 0.95 if form_type == "الصور النانوية (Nano-Systems)" else 0.70

    pk_results = {
        'Time': t_points,
        'Reference': calculate_pk_profile(t_points, dose_mg, 0.65, 1.5, ke, Vd),
        t1_name: calculate_pk_profile(t_points, dose_mg, f_nano, ka_nano, ke, Vd),
        t2_name: calculate_pk_profile(t_points, dose_mg, f_nano*0.85, ka_nano*0.6, ke, Vd),
        t3_name: calculate_pk_profile(t_points, dose_mg, 0.68, 1.6, ke, Vd)
    }
    
    df = pd.DataFrame(pk_results)
    for col in df.columns[1:]:
        df[col] = df[col] * np.random.normal(1, 0.03, len(t_points))

    with tab_comparison:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader(f"📈 منحنى تركيز البلازما المقارن (In-Vivo Profiles)")
        
        col_plot, col_metrics = st.columns([2, 1])
        
        with col_plot:
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#475569', '#2563eb', '#f59e0b', '#10b981']
            for i, col in enumerate(df.columns[1:]):
                style = '--' if col == 'Reference' else '-'
                ax.plot(df['Time'], df[col], marker='o', label=col, color=colors[i], linestyle=style, linewidth=2.5 if i==1 else 1.5)
            
            ax.set_xlabel("Time (Hours)")
            ax.set_ylabel("Concentration (μg/mL)")
            ax.grid(True, alpha=0.2)
            ax.legend()
            st.pyplot(fig)
            
        with col_metrics:
            st.subheader("🎯 نتائج In-Vivo المستخرجة")
            auc_ref = get_auc(df['Reference'], df['Time'])
            
            for col in [t1_name, t2_name, t3_name]:
                idx_max = df[col].idxmax()
                cmax = df[col].max()
                tmax = df.iloc[idx_max]['Time']
                auc_test = get_auc(df[col], df['Time'])
                ratio = (auc_test / auc_ref) * 100
                
                ci_low, ci_high = ratio * 0.95, ratio * 1.05
                is_be = 80 <= ci_low and ci_high <= 125

                with st.expander(f"نتائج {col}", expanded=True):
                    c_m1, c_m2 = st.columns(2)
                    c_m1.markdown(f"<p class='metric-label'>Cmax</p><p class='metric-value'>{cmax:.2f}</p>", unsafe_allow_html=True)
                    c_m2.markdown(f"<p class='metric-label'>Tmax (h)</p><p class='metric-value'>{tmax:.2f}</p>", unsafe_allow_html=True)
                    
                    st.write(f"**نسبة AUC:** {ratio:.2f}%")
                    status = "متكافئ حيوياً ✅" if is_be else "غير متكافئ ❌"
                    cls = "status-pass" if is_be else "status-fail"
                    st.markdown(f"<span class='{cls}'>{status}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_pharma:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("🧪 تحليل المواد المضافة والشكل الصيدلاني")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**الشكل الصيدلاني:**", form_type)
            st.write("**المواد المضافة المستخدمة:**")
            for exc in selected_excipients:
                st.markdown(f"- `{exc}`")
        with c2:
            if form_type == "الصور النانوية (Nano-Systems)":
                st.metric("حجم الجسيمات (Target Particle Size)", f"{particle_size} nm")
                st.info("تأثير حجم الجسيمات: الحجم الأصغر يزيد مساحة السطح ويحسن سرعة الذوبان والـ Cmax.")
        
        st.divider()
        st.write("**توقع الأداء المختبري (In-Vitro Expectations):**")
        st.table(pd.DataFrame({
            "المعيار": ["زمن التفتت", "معدل الذوبان Q-15", "الاستقرارية"],
            t1_name: ["0.5 min", "98.5%", "عالية"],
            t2_name: ["4.2 min", "82.1%", "متوسطة"],
            t3_name: ["15.0 min", "65.4%", "قياسية"]
        }))
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_library:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📚 مكتبة المراجع والمنظمات الدولية (Full Access)")
        
        for category, items in REGULATORY_LIBRARY.items():
            st.markdown(f"#### 🏛️ {category}")
            for item in items:
                st.markdown(f"🔗 <a href='{item['url']}' class='ref-link' target='_blank'>{item['title']}</a>", unsafe_allow_html=True)
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_report:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📄 التقرير التحليلي النهائي")
        report = f"""
        **Sama Pharma Tech - Bioequivalence Final Report**
        ---
        - **المادة الفعالة:** {api_name}
        - **الشكل الصيدلاني:** {form_type}
        - **المواد المضافة:** {', '.join(selected_excipients)}
        - **عدد المتطوعين:** {subjects}
        
        **التوصية الفنية:**
        أظهرت النتائج أن التركيبة **({t1_name})** هي الأفضل من حيث الـ In-vivo Performance، خاصة عند استخدام {selected_excipients[0] if selected_excipients else 'ناقلات متطورة'}.
        """
        st.markdown(report)
        st.download_button("📥 تحميل ملف النتائج الكاملة", df.to_csv(), "Sama_Full_Analysis.csv")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("💡 يرجى ضبط البروتوكول واختيار المواد المضافة، ثم اضغط على 'تشغيل التحليل المتكامل' لعرض النتائج.")

st.divider()
st.caption("© 2024 Sama Pharma Tech | Research & Development Division")