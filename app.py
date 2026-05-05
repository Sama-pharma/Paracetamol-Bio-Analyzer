import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(
    page_title="Sama Pharma Tech | Global Bioequivalence Hub",
    page_icon="🧬",
    layout="wide"
)

# --- Enhanced Visual Styling (CSS) ---
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
    .reference-section { border: 2px solid #1e3a8a; background-color: #f0f4ff; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
    .protocol-tag { background: #fef3c7; color: #92400e; padding: 2px 10px; border-radius: 5px; font-size: 0.85rem; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- Comprehensive Pharmaceutical Database ---
PHARMA_DATA = {
    "dosage_forms": [
        "أقراص (Tablets)", 
        "كبسولات جيلاتينية صلبة", 
        "كبسولات جيلاتينية رخوة (Softgels)", 
        "شراب (Syrup)", 
        "معلق (Suspension)", 
        "حقن (Ampoules/Vials)", 
        "نانو (Nano-Formulation)", 
        "أقراص ممتدة المفعول (SR/ER)",
        "جيل (Gel/Topical)",
        "لبوس (Suppositories)"
    ],
    "excipients": {
        "أقراص/كبسولات": [
            "Lactose Monohydrate", "Microcrystalline Cellulose (MCC)", "Magnesium Stearate", 
            "PVP K30", "Crospovidone", "HPMC", "Starch", "Talc", "Colloidal Silicon Dioxide",
            "Sodium Starch Glycolate", "Stearic Acid", "Ethyl Cellulose"
        ],
        "شراب/معلق": [
            "Glycerin", "Xanthan Gum", "Tween 80 (Polysorbate)", "Sorbitol", 
            "Sodium Benzoate", "Sucrose", "Propylene Glycol", "CMC-Na", "Aspartame",
            "Citric Acid", "Methylparaben"
        ],
        "حقن": [
            "Saline (0.9% NaCl)", "PEG 400", "Polysorbate 80", "Ethanol", 
            "Phosphate Buffer", "Water for Injection", "Benzyl Alcohol", "Dextrose"
        ],
        "نانو": [
            "Chitosan Nanoparticles", "PLGA Polymers", "Phospholipids (Liposomes)", 
            "PEGylated Lipids", "Solid Lipid Nanoparticles (SLN)", "Gold Nanoparticles", 
            "Mesoporous Silica", "Albumin Nanoparticles", "Poloxamer 188", "DOPC"
        ]
    },
    "study_models": [
        "Human Volunteers (متطوعين بشر)",
        "Beagle Dogs",
        "Rabbits (New Zealand)",
        "Rats (Wistar/SD)",
        "Mice",
        "Mini-Pigs"
    ],
    "drug_specific_refs": {
        "Paracetamol": "https://www.accessdata.fda.gov/scripts/cder/ob/results_product.cfm?Appl_Type=N&Appl_No=006456",
        "Atorvastatin": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2009/020702s057lbl.pdf",
        "Metformin": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2017/020357s037s039lbl.pdf",
        "Ibuprofen": "https://www.accessdata.fda.gov/scripts/cder/ob/results_product.cfm?Appl_Type=N&Appl_No=017463"
    }
}

# --- Global Regulatory & Research Library ---
REGULATORY_LIBRARY = {
    "المنظمات والهيئات الرقابية (Regulatory Authorities)": [
        {"title": "FDA - Center for Drug Evaluation and Research (CDER)", "url": "https://www.fda.gov/about-fda/center-drug-evaluation-and-research-cder"},
        {"title": "EMA - Guideline on the Investigation of Bioequivalence", "url": "https://www.ema.europa.eu/en/investigation-bioequivalence-scientific-guideline"},
        {"title": "WHO - Prequalification of Medicines Programme", "url": "https://extranet.who.int/pqweb/medicines"},
        {"title": "SFDA - Saudi Food and Drug Authority BE Guidelines", "url": "https://www.sfda.gov.sa/en/regulations?tags=8"},
        {"title": "ICH M13A - Bioequivalence Standards (2024-2025)", "url": "https://www.ich.org/page/multidisciplinary-guidelines"}
    ],
    "المكتبات البحثية التخصصية (Scientific Research)": [
        {"title": "PubMed - Bioavailability & Bioequivalence Research", "url": "https://pubmed.ncbi.nlm.nih.gov/?term=bioequivalence"},
        {"title": "ScienceDirect - Journal of Controlled Release", "url": "https://www.sciencedirect.com/journal/journal-of-controlled-release"},
        {"title": "Google Scholar - Advanced Drug Delivery Reviews", "url": "https://scholar.google.com/"},
        {"title": "AAPS Journal - Pharmaceutical Sciences Research", "url": "https://www.aaps.org/publications/aaps-journals"}
    ]
}

# --- Scientific Simulation Engine ---
def generate_pk_data(t, dose, f, ka, ke, vd, weight):
    """Calculates Plasma Concentration taking into account Body Weight with high precision."""
    # Vd calculation (L/kg) - weight impact
    effective_vd = vd * weight
    # Mathematical stabilization for identical rates
    if abs(ka - ke) < 0.001: ka += 0.01
    
    # Bateman Equation for 1-Compartment Oral Absorption
    conc = (f * dose * ka / (effective_vd * (ka - ke))) * (np.exp(-ke * t) - np.exp(-ka * t))
    return np.maximum(0, conc)

def get_auc(conc, time):
    """Calculates Area Under the Curve (AUC) using trapezoidal rule."""
    try:
        # Use trapezoid if available (newer numpy), fallback to trapz
        if hasattr(np, 'trapezoid'):
            return np.trapezoid(conc, time)
        return np.trapz(conc, time)
    except Exception:
        return 0.0

# --- UI Header ---
st.markdown("<h1 class='main-header'>🧬 Sama Pharma Tech | Bioequivalence Precision Hub</h1>", unsafe_allow_html=True)

tab_setup, tab_analysis, tab_library, tab_report = st.tabs([
    "⚙️ إعدادات الدراسة", 
    "📊 تحليل النتائج (In-Vivo)", 
    "📚 المكتبة العلمية والمراجع",
    "📄 التقارير النهائية"
])

with tab_setup:
    col_main1, col_main2 = st.columns(2)
    with col_main1:
        st.subheader("📝 تفاصيل الدواء المرجعي (RLD)")
        api_name = st.selectbox("اختر المادة الفعالة (API)", list(PHARMA_DATA["drug_specific_refs"].keys()) + ["Custom"])
        if api_name == "Custom":
            api_name = st.text_input("اسم المادة المخصصة", "MyAPI")
            
        ref_drug = st.text_input("اسم الدواء العالمي المرجعي", "Reference Innovator®")
        total_dose = st.number_input("الجرعة الكلية (mg)", value=500.0, step=50.0)
        
        # Reference drug specific reference link
        ref_url = PHARMA_DATA["drug_specific_refs"].get(api_name, "https://www.accessdata.fda.gov/scripts/cder/ob/default.cfm")
        st.markdown(f"🔗 [رابط مرجع الدواء المرجعي (FDA/EMA)]({ref_url})")
        
    with col_main2:
        st.subheader("👥 نموذج الدراسة (Study Model)")
        study_model = st.selectbox("نوع الكائن / المتطوعين", PHARMA_DATA["study_models"])
        
        c1, c2 = st.columns(2)
        with c1:
            avg_weight = st.number_input("متوسط الوزن (kg)", value=70.0 if "Human" in study_model else 0.25, step=0.1)
        with c2:
            feeding_status = st.radio("الحالة الغذائية", ["صائم (Fasted)", "فاطر (Fed)"], horizontal=True)
            
        num_subjects = st.slider("عدد العينات (N)", 6, 60, 12)

    st.divider()
    st.subheader("🧪 تخصيص التركيبات المختبرة (Triple Comparison)")
    
    t_cols = st.columns(3)
    formulations = {}
    
    for i, col in enumerate(t_cols, 1):
        with col:
            st.markdown(f"### 🧪 تركيبة مختبرة {i}")
            name = st.text_input(f"اسم المنتج {i}", f"Sama-Formula-{i}", key=f"name_{i}")
            form = st.selectbox(f"الصورة الصيدلانية {i}", PHARMA_DATA["dosage_forms"], key=f"form_{i}")
            
            # Map excipients based on form
            if "نانو" in form: exc_cat = "نانو"
            elif "حقن" in form: exc_cat = "حقن"
            elif "شراب" in form or "معلق" in form: exc_cat = "شراب/معلق"
            else: exc_cat = "أقراص/كبسولات"
            
            selected_excs = st.multiselect(f"المواد المضافة {i}", PHARMA_DATA["excipients"][exc_cat], key=f"excs_{i}")
            
            p_size = 0
            if "نانو" in form:
                p_size = st.number_input(f"حجم الجسيمات (nm) - {i}", value=120, key=f"ps_{i}")
                st.markdown(f"<span class='nano-badge'>تكنولوجيا النانو مفعلة: {p_size} nm</span>", unsafe_allow_html=True)
            
            formulations[name] = {"form": form, "excipients": selected_excs, "particle_size": p_size}

    run_analysis = st.button("🚀 تشغيل تحليل التكافؤ الحيوي الشامل")

if "df_results" not in st.session_state:
    st.session_state.df_results = None

if run_analysis:
    t_points = np.linspace(0, 24, 100) # Higher resolution for smoother curves
    
    # Basic PK parameters based on model
    is_human = "Human" in study_model
    Vd_base = 0.65 if is_human else 0.85 # L/kg
    ke = 0.18 if is_human else 0.35      
    
    # Simulate Reference with corrected variation
    f_ref = 0.85 if "فاطر" in feeding_status else 0.75
    ka_ref = 1.2 if "فاطر" in feeding_status else 1.8
    ref_conc = generate_pk_data(t_points, total_dose, f_ref, ka_ref, ke, Vd_base, avg_weight)
    
    # Add minor biological noise to reference to simulate real in-vivo data
    ref_noise = 0.02 * np.random.normal(0, 1, len(t_points))
    ref_conc = np.maximum(0, ref_conc + ref_noise)
    
    results = {'Time': t_points, 'Reference (RLD)': ref_conc}
    
    # Simulate Test Formulations
    for name, data in formulations.items():
        f_val, ka_val = f_ref, ka_ref
        
        # Impact of Formulation Type
        if "نانو" in data['form']:
            f_val = 0.95 if data['particle_size'] < 100 else 0.88
            ka_val = 4.5 if data['particle_size'] < 100 else 3.2
        elif "حقن" in data['form']:
            f_val = 1.0; ka_val = 12.0
        elif "SR" in data['form']:
            f_val = 0.82; ka_val = 0.25
        elif "شراب" in data['form'] or "جيل" in data['form']:
            ka_val = 2.5
            
        test_conc = generate_pk_data(t_points, total_dose, f_val, ka_val, ke, Vd_base, avg_weight)
        
        # Add Biological Variability (In-Vivo Simulation)
        noise_level = 0.12 if is_human else 0.22 
        variability = noise_level / np.sqrt(num_subjects)
        test_conc = test_conc * np.random.normal(1, variability, len(t_points))
        results[name] = np.maximum(0, test_conc)
    
    st.session_state.df_results = pd.DataFrame(results)
    st.session_state.formulations = formulations
    st.success("تم الانتهاء من محاكاة النتائج وتحسين دقة المرجع!")

if st.session_state.df_results is not None:
    df = st.session_state.df_results
    
    with tab_analysis:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📈 منحنيات التكافؤ الحيوي (Comparative PK Profiles)")
        st.markdown(f"""
            <span class='protocol-tag'>النموذج: {study_model}</span>
            <span class='protocol-tag'>الوزن: {avg_weight} kg</span>
            <span class='protocol-tag'>الحالة: {feeding_status}</span>
        """, unsafe_allow_html=True)
        
        col_plot, col_metrics = st.columns([2, 1])
        
        with col_plot:
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#1e3a8a', '#2563eb', '#f59e0b', '#10b981', '#ef4444']
            for i, col in enumerate(df.columns[1:]):
                style = '--' if 'Reference' in col else '-'
                width = 4 if 'Reference' in col else 2.5
                ax.plot(df['Time'], df[col], label=col, color=colors[i % len(colors)], linewidth=width)
            
            ax.set_xlabel("Time (Hours)", fontweight='bold')
            ax.set_ylabel("Plasma Conc. (μg/mL)", fontweight='bold')
            ax.set_title(f"Bioequivalence Comparison: {api_name}", fontsize=14, fontweight='bold', color='#1e3a8a')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            
        with col_metrics:
            st.markdown("### 🎯 المقاييس الحيوية المحسوبة")
            
            # Reference Metrics
            ref_col = df.columns[1]
            cmax_ref = df[ref_col].max()
            tmax_ref = df.iloc[df[ref_col].idxmax()]['Time']
            auc_ref = get_auc(df[ref_col].values, df['Time'].values)
            
            st.markdown(f"<div class='reference-section'>", unsafe_allow_html=True)
            st.markdown(f"**🏅 المرجع: {ref_drug}**")
            rm1, rm2, rm3 = st.columns(3)
            rm1.markdown(f"<p class='metric-label'>Cmax</p><p class='metric-value'>{cmax_ref:.2f}</p>", unsafe_allow_html=True)
            rm2.markdown(f"<p class='metric-label'>Tmax</p><p class='metric-value'>{tmax_ref:.1f}</p>", unsafe_allow_html=True)
            rm3.markdown(f"<p class='metric-label'>AUC</p><p class='metric-value'>{auc_ref:.1f}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.divider()
            
            # Test Metrics
            for col in df.columns[2:]:
                c_test = df[col].max()
                t_test = df.iloc[df[col].idxmax()]['Time']
                a_test = get_auc(df[col].values, df['Time'].values)
                ratio = (a_test / auc_ref) * 100 if auc_ref > 0 else 0
                
                with st.expander(f"نتائج {col}", expanded=True):
                    m1, m2, m3 = st.columns(3)
                    m1.markdown(f"<p class='metric-label'>Cmax</p><p class='metric-value'>{c_test:.2f}</p>", unsafe_allow_html=True)
                    m2.markdown(f"<p class='metric-label'>Tmax</p><p class='metric-value'>{t_test:.1f}</p>", unsafe_allow_html=True)
                    m3.markdown(f"<p class='metric-label'>AUC</p><p class='metric-value'>{a_test:.1f}</p>", unsafe_allow_html=True)
                    
                    is_be = 80 <= ratio <= 125
                    status = "متكافئ ✅" if is_be else "غير متكافئ ❌"
                    cls = "status-pass" if is_be else "status-fail"
                    st.markdown(f"<center><span class='{cls}'>{status} ({ratio:.1f}%)</span></center>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_library:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📚 المراجع والمكتبات العلمية")
        for cat, items in REGULATORY_LIBRARY.items():
            st.markdown(f"#### 🏷️ {cat}")
            for item in items:
                st.markdown(f"🔗 <a href='{item['url']}' class='ref-link' target='_blank'>{item['title']}</a>", unsafe_allow_html=True)
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_report:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📄 التقرير الفني النهائي (Technical Summary)")
        st.markdown(f"**نموذج الدراسة:** {study_model} | **متوسط الوزن:** {avg_weight} kg | **الحالة:** {feeding_status}")
        st.markdown(f"**المرجع:** {ref_drug} | AUC: {auc_ref:.2f} | Cmax: {cmax_ref:.2f}")
        
        rep_df = []
        for name, data in st.session_state.formulations.items():
            c_val = df[name].max()
            a_val = get_auc(df[name].values, df['Time'].values)
            rep_df.append({
                "المنتج": name,
                "الصورة الصيدلانية": data['form'],
                "النانو (nm)": data['particle_size'] if data['particle_size'] > 0 else "-",
                "Cmax (μg/mL)": f"{c_val:.2f}",
                "AUC (0-t)": f"{a_val:.2f}",
                "نسبة التكافؤ %": f"{(a_val/auc_ref)*100:.1f}%" if auc_ref > 0 else "0%"
            })
        st.table(pd.DataFrame(rep_df))
        st.download_button("📥 تحميل النتائج (CSV)", df.to_csv(index=False), "Sama_Full_Report.csv")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("💡 يرجى إدخال بيانات الدراسة والتركيبات ثم الضغط على 'تشغيل التحليل'.")

st.divider()
st.caption("Developed by Sama Pharma Tech | R&D Hub v8.0 - Precision In-Vivo Simulation Fixed")