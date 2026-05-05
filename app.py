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

# --- التنسيق البصري (CSS) المطور ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-header { color: #1e3a8a; text-align: center; font-weight: 800; font-size: 2.8rem; margin-bottom: 20px; border-bottom: 4px solid #2563eb; padding-bottom: 10px; }
    .section-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; margin-bottom: 25px; }
    .status-pass { background-color: #dcfce7; color: #166534; padding: 8px 20px; border-radius: 50px; font-weight: bold; display: inline-block; border: 1px solid #166534; }
    .status-fail { background-color: #fee2e2; color: #991b1b; padding: 8px 20px; border-radius: 50px; font-weight: bold; display: inline-block; border: 1px solid #991b1b; }
    .ref-link { color: #2563eb; text-decoration: none; font-weight: 600; display: block; margin-bottom: 12px; border-right: 4px solid #2563eb; padding-right: 15px; background: #f8fafc; padding-top: 10px; padding-bottom: 10px; border-radius: 0 8px 8px 0; }
    .metric-label { color: #64748b; font-size: 0.9rem; font-weight: bold; margin-bottom: 2px; }
    .metric-value { color: #1e293b; font-size: 1.2rem; font-weight: 800; }
    .nano-badge { background-color: #eff6ff; color: #1e40af; padding: 4px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: bold; }
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
    "الهيئات الرقابية الدولية (Regulatory Bodies)": [
        {"title": "FDA - Orange Book: Approved Drug Products", "url": "https://www.accessdata.fda.gov/scripts/cder/ob/index.cfm"},
        {"title": "EMA - Clinical Pharmacology Guidelines", "url": "https://www.ema.europa.eu/en/human-regulatory/research-development/scientific-guidelines/clinical-pharmacology-pharmacokinetics"},
        {"title": "WHO - Guidance on Bioequivalence Studies (TRS 1003)", "url": "https://www.who.int/medicines/publications/pharmprep/WHO_TRS_1003_Annex6.pdf"},
        {"title": "ICH M13A - International Bioequivalence Standard 2024", "url": "https://database.ich.org/sites/default/files/ICH_M13A_Step4_Guideline_2024_0611.pdf"}
    ],
    "المكتبات البحثية (Scientific Databases)": [
        {"title": "PubMed: Bioavailability & Nano-tech Research", "url": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"title": "ScienceDirect: Advanced Drug Delivery Reviews", "url": "https://www.sciencedirect.com/journal/advanced-drug-delivery-reviews"},
        {"title": "Google Scholar: Comparative BE Studies 2025", "url": "https://scholar.google.com/"},
        {"title": "Journal of Controlled Release: Nano-Bio Systems", "url": "https://www.journals.elsevier.com/journal-of-controlled-release"}
    ]
}

# --- محرك المحاكاة العلمي المطور ---
def generate_pk_data(t, dose, f, ka, ke, vd):
    """حساب منحنى تركيز البلازما باستخدام نموذج الغرفة الواحدة"""
    if abs(ka - ke) < 0.001: ka += 0.01
    # معادلة التركيز القياسية
    conc = (f * dose * ka / (vd * (ka - ke))) * (np.exp(-ke * t) - np.exp(-ka * t))
    return np.maximum(0, conc)

def get_auc(conc, time):
    """حساب المساحة تحت المنحنى بدقة عالية"""
    try:
        # الإصدارات الحديثة من numpy تستخدم trapezoid
        return np.trapezoid(conc, time)
    except AttributeError:
        # التوافق مع الإصدارات الأقدم
        return np.trapz(conc, time)

# --- واجهة المستخدم الرئيسية ---
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
        api_name = st.text_input("اسم المادة الفعالة (API)", "Paracetamol")
        ref_drug = st.text_input("الدواء العالمي المرجعي (RLD)", "Panadol® (Reference)")
        total_dose = st.number_input("الجرعة الكلية (mg)", value=500.0, step=50.0)
        
    with col_main2:
        st.subheader("👥 معايير الدراسة الإحصائية")
        num_subjects = st.slider("عدد المتطوعين في الدراسة (N)", 12, 120, 24)
        study_design = st.selectbox("تصميم الدراسة", ["Crossover (2x2)", "Parallel", "Replicate Design"])

    st.divider()
    st.subheader("🧪 تخصيص المقارنة الثلاثية (Comparative Formulation Lab)")
    
    t_cols = st.columns(3)
    formulations = {}
    
    for i, col in enumerate(t_cols, 1):
        with col:
            st.markdown(f"### 🧪 التركيبة {i}")
            name = st.text_input(f"اسم المنتج {i}", f"Test-Formula-{i}", key=f"name_{i}")
            form = st.selectbox(f"الصورة الصيدلانية {i}", PHARMA_DATA["الأشكال الصيدلانية"], key=f"form_{i}")
            
            # اختيار فئة المواد المضافة بناء على الشكل
            if "نانو" in form: exc_cat = "النانو (Nano-Carriers)"
            elif "حقن" in form: exc_cat = "الحقن (Injectables)"
            elif "شراب" in form or "معلق" in form: exc_cat = "السائلة (شراب/معلق)"
            else: exc_cat = "الصلبة (أقراص/كبسولات)"
            
            selected_excs = st.multiselect(f"المواد المضافة {i}", PHARMA_DATA["المواد المضافة"][exc_cat], key=f"excs_{i}")
            
            p_size = 0
            if "نانو" in form:
                p_size = st.number_input(f"حجم الجسيمات (nm) - {i}", value=150, help="الحجم يؤثر على سرعة الامتصاص و Cmax", key=f"ps_{i}")
                st.markdown(f"<span class='nano-badge'>تقنية النانو نشطة: {p_size} nm</span>", unsafe_allow_html=True)
            
            formulations[name] = {"form": form, "excipients": selected_excs, "particle_size": p_size}

    run_analysis = st.button("🚀 تشغيل تحليل التكافؤ الحيوي والمقارنة الثلاثية")

if "df_results" not in st.session_state:
    st.session_state.df_results = None

if run_analysis:
    # نقاط زمنية مكثفة لتحسين الرسم البياني
    t_points = np.array([0, 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 10, 12, 18, 24])
    Vd = 0.7 * 70  # حجم التوزيع الافتراضي (L)
    ke = 0.15      # ثابت الإخراج (1/h)
    
    # محاكاة الدواء المرجعي
    ref_conc = generate_pk_data(t_points, total_dose, 0.75, 1.5, ke, Vd)
    results = {'Time': t_points, 'Reference (RLD)': ref_conc}
    
    # محاكاة التركيبات الثلاث بناء على المدخلات العلمية
    for name, data in formulations.items():
        f_val, ka_val = 0.75, 1.5
        
        # منطق تأثير الأشكال الصيدلانية
        if "نانو" in data['form']:
            # جسيمات أصغر = امتصاص أسرع وتوافر أعلى بكثير
            f_val = 0.98 if data['particle_size'] < 100 else 0.88
            ka_val = 5.0 if data['particle_size'] < 100 else 3.5
        elif "حقن" in data['form']:
            f_val = 1.0
            ka_val = 15.0 # امتصاص شبه فوري
        elif "SR" in data['form']:
            f_val = 0.80
            ka_val = 0.2 # امتصاص بطيء جداً
        elif "شراب" in data['form']:
            ka_val = 2.5
            
        test_conc = generate_pk_data(t_points, total_dose, f_val, ka_val, ke, Vd)
        
        # إضافة تباين إحصائي (Inter-subject variability)
        noise = (0.12 / np.sqrt(num_subjects)) 
        test_conc = test_conc * np.random.normal(1, noise, len(t_points))
        results[name] = np.maximum(0, test_conc)
    
    st.session_state.df_results = pd.DataFrame(results)
    st.session_state.formulations = formulations
    st.success("تم الانتهاء من تحليل البيانات بنجاح!")

if st.session_state.df_results is not None:
    df = st.session_state.df_results
    
    with tab_analysis:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📈 منحنيات التركيز الدوائي (Plasma Concentration Profiles)")
        
        col_plot, col_metrics = st.columns([2, 1])
        
        with col_plot:
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#1e3a8a', '#2563eb', '#f59e0b', '#10b981', '#ef4444']
            for i, col in enumerate(df.columns[1:]):
                style = '--' if 'Reference' in col else '-'
                width = 4 if 'Reference' in col else 2.5
                ax.plot(df['Time'], df[col], label=col, marker='o', linestyle=style, color=colors[i % len(colors)], linewidth=width, markersize=4)
            
            ax.set_xlabel("Time (Hours)", fontweight='bold')
            ax.set_ylabel("Concentration (μg/mL)", fontweight='bold')
            ax.set_title(f"Bioequivalence Study: {api_name}", fontsize=14, fontweight='bold', color='#1e3a8a')
            ax.grid(True, which='both', linestyle='--', alpha=0.5)
            ax.legend(frameon=True, shadow=True)
            st.pyplot(fig)
            
        with col_metrics:
            st.markdown("### 🎯 المقاييس الحيوية (PK Parameters)")
            auc_ref = get_auc(df.iloc[:, 1], df['Time'])
            
            for col in df.columns[2:]:
                cmax = df[col].max()
                tmax = df.iloc[df[col].idxmax()]['Time']
                auc_test = get_auc(df[col], df['Time'])
                be_ratio = (auc_test / auc_ref) * 100
                
                with st.expander(f"التحليل التفصيلي: {col}", expanded=True):
                    m1, m2 = st.columns(2)
                    m1.markdown(f"<p class='metric-label'>Cmax</p><p class='metric-value'>{cmax:.2f}</p>", unsafe_allow_html=True)
                    m2.markdown(f"<p class='metric-label'>Tmax (h)</p><p class='metric-value'>{tmax:.1f}</p>", unsafe_allow_html=True)
                    
                    st.write(f"**نسبة AUC المقارنة:** {be_ratio:.1f}%")
                    is_be = 80 <= be_ratio <= 125
                    status = "متكافئ حيوياً ✅" if is_be else "غير متكافئ ❌"
                    cls = "status-pass" if is_be else "status-fail"
                    st.markdown(f"<center><span class='{cls}'>{status}</span></center>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_library:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📚 المراجع والمكتبات العلمية الموثقة")
        st.info("تم ربط هذه المراجع مباشرة بقواعد البيانات العالمية لضمان دقة البحث العلمي.")
        
        for cat, items in REGULATORY_LIBRARY.items():
            st.markdown(f"#### 🏷️ {cat}")
            for item in items:
                st.markdown(f"🔗 <a href='{item['url']}' class='ref-link' target='_blank'>{item['title']}</a>", unsafe_allow_html=True)
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_report:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📄 التقرير الفني الشامل لنتائج البحث")
        
        st.write(f"**المادة الخاضعة للدراسة:** {api_name}")
        st.write(f"**الدواء المرجعي المستخدم:** {ref_drug}")
        st.write(f"**تاريخ التحليل:** 2026-05-05")
        
        report_data = []
        for name, data in st.session_state.formulations.items():
            report_data.append({
                "التركيبة": name,
                "الصورة الصيدلانية": data['form'],
                "تقنية النانو (nm)": data['particle_size'] if data['particle_size'] > 0 else "غير مفعلة",
                "مواد التحميل": ", ".join(data['excipients'])
            })
        
        st.dataframe(pd.DataFrame(report_data), use_container_width=True)
        
        st.warning("⚠️ ملاحظة: هذه النتائج مبنية على نماذج محاكاة رياضية متقدمة (In-Silico Modeling) ويجب تأكيدها بتجارب سريرية نهائية.")
        st.download_button("📥 تحميل التقرير بصيغة CSV", df.to_csv(index=False), "Sama_Pharma_BE_Report.csv")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("💡 للبدء: قم بإدخال بيانات التركيبات في التبويب الأول واضغط على زر 'تشغيل التحليل'.")

st.divider()
st.caption("Developed by Sama Pharma Tech | Precision Research & Development Hub v5.0")