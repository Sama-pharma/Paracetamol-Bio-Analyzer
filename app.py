import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="Sama Pharma Tech | Global Bioequivalence Hub",
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
    .metric-label { color: #64748b; font-size: 0.85rem; font-weight: bold; margin-bottom: 2px; }
    .metric-value { color: #1e293b; font-size: 1.1rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- قاعدة بيانات شاملة للمواد المضافة والأشكال الصيدلانية ---
PHARMA_DATA = {
    "الأشكال الصيدلانية": [
        "أقراص (Tablets)", 
        "كبسولات جيلاتينية صلبة", 
        "كبسولات جيلاتينية رخوة (Softgels)", 
        "شراب (Syrup)", 
        "معلق (Suspension)", 
        "حقن (Ampoules/Vials)", 
        "نانو (Nano-Formulation)", 
        "أقراص ممتدة المفعول (SR/ER)",
        "جيل (Gel/Topical)"
    ],
    "المواد المضافة": {
        "الصلبة (أقراص/كبسولات)": [
            "Lactose Monohydrate", "Microcrystalline Cellulose (MCC)", "Magnesium Stearate", 
            "PVP K30", "Crospovidone", "HPMC", "Starch", "Talc", "Colloidal Silicon Dioxide"
        ],
        "السائلة (شراب/معلق)": [
            "Glycerin", "Xanthan Gum", "Tween 80 (Polysorbate)", "Sorbitol", 
            "Sodium Benzoate", "Sucrose", "Propylene Glycol", "CMC-Na"
        ],
        "الحقن (Injectables)": [
            "Saline (0.9% NaCl)", "PEG 400", "Polysorbate 80", "Ethanol", 
            "Phosphate Buffer", "Water for Injection", "Benzyl Alcohol"
        ],
        "النانو (Nano-Carriers)": [
            "Chitosan Nanoparticles", "PLGA Polymers", "Phospholipids (Liposomes)", 
            "PEGylated Lipids", "Solid Lipid Nanoparticles (SLN)", "Gold Nanoparticles", 
            "Mesoporous Silica", "Albumin Nanoparticles"
        ]
    }
}

# --- مكتبة المراجع والمنظمات العالمية المحدثة 2024-2025 ---
REGULATORY_LIBRARY = {
    "الهيئات الرقابية الدولية": [
        {"title": "FDA - Orange Book: Approved Drug Products with Therapeutic Equivalence", "url": "https://www.accessdata.fda.gov/scripts/cder/ob/index.cfm"},
        {"title": "EMA - Clinical Pharmacology and Bioequivalence Guidelines", "url": "https://www.ema.europa.eu/en/human-regulatory/research-development/scientific-guidelines/clinical-pharmacology-pharmacokinetics"},
        {"title": "WHO - Guidance on Bioequivalence Studies (TRS 1003)", "url": "https://www.who.int/medicines/publications/pharmprep/WHO_TRS_1003_Annex6.pdf"},
        {"title": "ICH M13A - Bioequivalence for Immediate-Release Solids", "url": "https://database.ich.org/sites/default/files/ICH_M13A_Step4_Guideline_2024_0611.pdf"}
    ],
    "المكتبات البحثية والأبحاث المتقدمة": [
        {"title": "PubMed: Bioavailability Improvement via Nano-technology", "url": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"title": "ScienceDirect: Advanced Drug Delivery Systems (ADDS)", "url": "https://www.sciencedirect.com/journal/advanced-drug-delivery-reviews"},
        {"title": "Google Scholar: Comparative Bioequivalence Studies 2025", "url": "https://scholar.google.com/"},
        {"title": "Journal of Controlled Release: Nano-Bio Interface", "url": "https://www.journals.elsevier.com/journal-of-controlled-release"}
    ]
}

# --- محرك المحاكاة العلمي المطور ---
def generate_pk_data(t, dose, f, ka, ke, vd):
    """حساب منحنى تركيز البلازما باستخدام نموذج الغرفة الواحدة"""
    if ka == ke: ka += 0.01
    conc = (f * dose * ka / (vd * (ka - ke))) * (np.exp(-ke * t) - np.exp(-ka * t))
    return np.maximum(0, conc)

def get_auc(conc, time):
    """إصلاح خطأ numpy trapz عبر استخدام trapezoid أو البديل المناسب"""
    try:
        # لمحاولة استخدام الإصدار الجديد
        return np.trapezoid(conc, time)
    except AttributeError:
        # التوافق مع الإصدارات الأقدم
        return np.trapz(conc, time)

# --- واجهة المستخدم ---
st.markdown("<h1 class='main-header'>🧬 Sama Pharma Tech | Precision Bioequivalence Hub</h1>", unsafe_allow_html=True)

tab_setup, tab_analysis, tab_library, tab_report = st.tabs([
    "⚙️ إعدادات الدراسة والتركيبات", 
    "📊 مقارنة النتائج (In-Vivo)", 
    "📚 المكتبة المرجعية والأبحاث",
    "📄 تقارير الجودة والنتائج"
])

with tab_setup:
    col_main1, col_main2 = st.columns(2)
    with col_main1:
        st.subheader("📝 تفاصيل الدواء المرجعي")
        api_name = st.text_input("اسم المادة الفعالة (API)", "Sama-Paracetamol")
        ref_drug = st.text_input("الدواء العالمي المرجعي (RLD)", "Panadol® (Reference)")
        total_dose = st.number_input("الجرعة الكلية (mg)", value=500.0)
        
    with col_main2:
        st.subheader("👥 معايير الدراسة الإحصائية")
        num_subjects = st.slider("عدد المتطوعين في الدراسة (N)", 12, 120, 24)
        sampling_frequency = st.selectbox("تردد أخذ العينات", ["مكثف (12 نقطة)", "قياسي (8 نقاط)", "مختصر (5 نقاط)"])

    st.divider()
    st.subheader("💊 تخصيص التركيبات الثلاث (Comparative Analysis)")
    
    t_cols = st.columns(3)
    formulations = {}
    
    for i, col in enumerate(t_cols, 1):
        with col:
            st.markdown(f"### 🧪 التركيبة المختبرة {i}")
            name = st.text_input(f"اسم المنتج {i}", f"Test-Formula-{i}", key=f"name_{i}")
            form = st.selectbox(f"الصورة الصيدلانية {i}", PHARMA_DATA["الأشكال الصيدلانية"], key=f"form_{i}")
            
            # فلترة المواد المضافة بناء على الشكل
            if "نانو" in form: exc_cat = "النانو (Nano-Carriers)"
            elif "حقن" in form: exc_cat = "الحقن (Injectables)"
            elif "شراب" in form or "معلق" in form: exc_cat = "السائلة (شراب/معلق)"
            else: exc_cat = "الصلبة (أقراص/كبسولات)"
            
            selected_excs = st.multiselect(f"المواد المضافة {i}", PHARMA_DATA["المواد المضافة"][exc_cat], key=f"excs_{i}")
            
            p_size = 0
            if "نانو" in form:
                p_size = st.number_input(f"حجم الجسيمات (nm) - {i}", value=150, help="يؤثر الحجم مباشرة على سرعة الامتصاص و Cmax", key=f"ps_{i}")
            
            formulations[name] = {"form": form, "excipients": selected_excs, "particle_size": p_size}

    run_analysis = st.button("🚀 تشغيل تحليل التكافؤ الحيوي الشامل")

if "df_results" not in st.session_state:
    st.session_state.df_results = None

if run_analysis:
    # إعداد نقاط زمنية دقيقة
    t_points = np.array([0, 0.25, 0.5, 0.75, 1, 1.5, 2, 4, 6, 8, 12, 24])
    Vd = 0.7 * 70  # حجم التوزيع الافتراضي
    ke = 0.15      # ثابت الإخراج
    
    # محاكاة الدواء المرجعي
    ref_conc = generate_pk_data(t_points, total_dose, 0.65, 1.8, ke, Vd)
    results = {'Time': t_points, 'Reference (RLD)': ref_conc}
    
    # محاكاة التركيبات الثلاث بناء على المدخلات العلمية
    for name, data in formulations.items():
        # قيم افتراضية
        f_val, ka_val = 0.65, 1.8
        
        # تأثير الصورة الصيدلانية على الـ PK
        if "نانو" in data['form']:
            # جسيمات أصغر = امتصاص أسرع وتوافر أعلى
            f_val = 0.95 if data['particle_size'] < 100 else 0.85
            ka_val = 4.0 if data['particle_size'] < 100 else 3.0
        elif "حقن" in data['form']:
            f_val = 1.0
            ka_val = 10.0 # امتصاص لحظي
        elif "SR" in data['form']:
            f_val = 0.75
            ka_val = 0.25 # امتصاص بطيء ممتد
        elif "شراب" in data['form']:
            ka_val = 2.5
            
        test_conc = generate_pk_data(t_points, total_dose, f_val, ka_val, ke, Vd)
        # إضافة تباين إحصائي بناء على عدد المتطوعين
        noise_level = 0.15 / np.sqrt(num_subjects)
        results[name] = test_conc * np.random.normal(1, noise_level, len(t_points))
    
    st.session_state.df_results = pd.DataFrame(results)
    st.session_state.formulations = formulations

if st.session_state.df_results is not None:
    df = st.session_state.df_results
    
    with tab_analysis:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📈 مقارنة منحنيات التركيز (In-Vivo PK Profiles)")
        
        col_plot, col_metrics = st.columns([2, 1])
        
        with col_plot:
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#1e3a8a', '#2563eb', '#f59e0b', '#10b981', '#ef4444']
            for i, col in enumerate(df.columns[1:]):
                style = '--' if 'Reference' in col else '-'
                width = 3 if 'Reference' in col else 2
                ax.plot(df['Time'], df[col], label=col, marker='o', linestyle=style, color=colors[i % len(colors)], linewidth=width)
            
            ax.set_xlabel("Time (Hours)")
            ax.set_ylabel("Plasma Concentration (μg/mL)")
            ax.set_title(f"Bioequivalence Study: {api_name}", fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.2)
            ax.legend()
            st.pyplot(fig)
            
        with col_metrics:
            st.markdown("### 🎯 نتائج PK المستخلصة")
            auc_ref = get_auc(df.iloc[:, 1], df['Time'])
            
            for col in df.columns[2:]:
                cmax = df[col].max()
                tmax = df.iloc[df[col].idxmax()]['Time']
                auc_test = get_auc(df[col], df['Time'])
                be_ratio = (auc_test / auc_ref) * 100
                
                with st.expander(f"تحليل: {col}", expanded=True):
                    m1, m2 = st.columns(2)
                    m1.markdown(f"<p class='metric-label'>Cmax</p><p class='metric-value'>{cmax:.2f}</p>", unsafe_allow_html=True)
                    m2.markdown(f"<p class='metric-label'>Tmax (h)</p><p class='metric-value'>{tmax:.1f}</p>", unsafe_allow_html=True)
                    
                    st.write(f"**نسبة AUC:** {be_ratio:.1f}%")
                    is_be = 80 <= be_ratio <= 125
                    status = "متكافئ حيوياً ✅" if is_be else "غير متكافئ ❌"
                    cls = "status-pass" if is_be else "status-fail"
                    st.markdown(f"<span class='{cls}'>{status}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_library:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📚 المراجع والمكتبات العالمية المعتمدة")
        for cat, items in REGULATORY_LIBRARY.items():
            st.markdown(f"#### 🏛️ {cat}")
            for item in items:
                st.markdown(f"🔗 <a href='{item['url']}' class='ref-link' target='_blank'>{item['title']}</a>", unsafe_allow_html=True)
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_report:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📄 التقرير الفني النهائي")
        st.write(f"**المادة الفعالة:** {api_name} | **المرجع:** {ref_drug}")
        
        final_summary = []
        for name, data in st.session_state.formulations.items():
            final_summary.append({
                "التركيبة": name,
                "الشكل": data['form'],
                "حجم النانو (nm)": data['particle_size'] if data['particle_size'] > 0 else "N/A",
                "المواد المضافة": ", ".join(data['excipients'])
            })
        
        st.table(pd.DataFrame(final_summary))
        st.info("تم إنشاء هذا التقرير بناءً على محاكاة النمذجة الدوائية (Pharmacokinetic Modeling) المعتمدة.")
        st.download_button("📥 تحميل النتائج الكاملة (CSV)", df.to_csv(index=False), "Bioequivalence_Report.csv")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("💡 الرجاء تعبئة بيانات التركيبات في التبويب الأول ثم الضغط على 'تشغيل التحليل' لبدء المقارنة.")

st.divider()
st.caption("Developed by Sama Pharma Tech | R&D Excellence Hub v5.0")