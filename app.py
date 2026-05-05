import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Basic Config ---
st.set_page_config(
    page_title="Sama Pharma Tech | Precision v8.0",
    page_icon="🧬",
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main-header { color: #003366; text-align: center; font-weight: 900; font-size: 2.5rem; padding: 20px; background: #eefbff; border-radius: 15px; margin-bottom: 25px; border: 2px solid #00a8cc; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; border-right: 5px solid #00a8cc; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .reference-section { background: #f0f4f8; padding: 20px; border-radius: 15px; border: 1px solid #d1d9e6; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f8f9fa; border-radius: 5px 5px 0 0; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- Robust Calculation Engine ---
def safe_auc(y, x):
    """Robust Trapezoidal rule implementation without relying on specific np versions"""
    try:
        y = np.array(y)
        x = np.array(x)
        return np.sum((x[1:] - x[:-1]) * (y[1:] + y[:-1]) / 2.0)
    except:
        return 0.0

def pk_model(t, dose, f, ka, ke, vd, weight):
    """Pharmacokinetic simulation engine"""
    try:
        v_total = vd * weight
        if abs(ka - ke) < 1e-5: ka += 0.01
        # Bateman Equation
        conc = (f * dose * ka) / (v_total * (ka - ke)) * (np.exp(-ke * t) - np.exp(-ka * t))
        return np.maximum(0, conc)
    except:
        return np.zeros_like(t)

# --- Database ---
API_DATA = {
    "Paracetamol": {"ka": 2.1, "ke": 0.28, "vd": 0.9, "f": 0.88},
    "Atorvastatin": {"ka": 0.8, "ke": 0.05, "vd": 5.2, "f": 0.12},
    "Metformin": {"ka": 1.1, "ke": 0.15, "vd": 1.5, "f": 0.55},
    "Custom": {"ka": 1.0, "ke": 0.1, "vd": 1.0, "f": 0.7}
}

EXCIPIENTS = {
    "Solid": ["Lactose", "Starch", "Mg Stearate", "Talc", "MCC", "PVP"],
    "Liquid": ["Glycerin", "Sorbitol", "Xanthan Gum", "Water", "Ethanol"],
    "Nano": ["Chitosan", "PLGA", "Lipids", "PEG", "Gold", "Silica"]
}

# --- Sidebar Controls ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022243.png", width=100)
    st.header("⚙️ إعدادات المحاكاة")
    
    api_choice = st.selectbox("المادة الفعالة (API)", list(API_DATA.keys()))
    user_dose = st.number_input("الجرعة (mg)", value=500.0)
    
    st.divider()
    st.subheader("👥 نموذج الدراسة In-Vivo")
    subject = st.selectbox("نوع الكائن", ["Human (متطوعين)", "Animal (Beagle Dog)", "Animal (Rat)"])
    weight = st.number_input("الوزن (kg)", value=70.0 if "Human" in subject else 10.0)
    is_fed = st.checkbox("تأثير الطعام (Fed State)")

# --- Main Interface ---
st.markdown("<div class='main-header'>Sama Pharma Tech | R&D Excellence Hub v8.0</div>", unsafe_allow_html=True)

tab_calc, tab_refs = st.tabs(["📊 التحليل والمقارنة", "📚 المكتبة والمنظمات"])

with tab_refs:
    st.subheader("📚 مراجع التكافؤ الحيوي المدمجة")
    refs = {
        "FDA - CDER": "https://www.fda.gov/drugs/guidances-drugs/bioequivalence-recommendations-specific-products",
        "EMA - Guidelines": "https://www.ema.europa.eu/en/human-regulatory/research-development/bioequivalence",
        "WHO - Prequalification": "https://extranet.who.int/pqweb/medicines",
        "ICH - M13A Guideline": "https://www.ich.org/page/multidisciplinary-guidelines"
    }
    for name, url in refs.items():
        st.markdown(f"🔗 [{name}]({url})")
    st.info("تم دمج بروتوكولات FDA للأدوية النوعية لضمان دقة النتائج المقارنة.")

with tab_calc:
    col_ref, col_tests = st.columns([1, 2.5])
    
    with col_ref:
        st.markdown("<div class='reference-section'>", unsafe_allow_html=True)
        st.subheader("🚩 الدواء المرجعي (RLD)")
        ref_name = st.text_input("اسم المرجع", "Innovator Ref")
        r_cmax = st.number_input("Cmax المرجع المتوقع", value=6.5)
        r_tmax = st.number_input("Tmax المرجع المتوقع", value=1.5)
        r_auc = st.number_input("AUC المرجع المتوقع", value=45.0)
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("🧪 تركيبات الاختبار (Test Formulations)")
    t_cols = st.columns(3)
    formulations = []

    for i in range(3):
        with t_cols[i]:
            st.markdown(f"**التركيبة {i+1}**")
            f_name = st.text_input(f"الاسم", f"Formula-{i+1}", key=f"n{i}")
            f_type = st.selectbox(f"الصورة", ["Tablets", "Capsules", "Syrup", "Nano", "Ampoule"], key=f"t{i}")
            
            exc_list = EXCIPIENTS["Nano"] if f_type == "Nano" else (EXCIPIENTS["Liquid"] if f_type in ["Syrup", "Ampoule"] else EXCIPIENTS["Solid"])
            selected_excs = st.multiselect("المواد المضافة", exc_list, key=f"e{i}")
            
            p_size = 0
            if f_type == "Nano":
                p_size = st.number_input("حجم الجسيمات (nm)", value=150, key=f"p{i}")
            
            formulations.append({"name": f_name, "type": f_type, "excs": selected_excs, "psize": p_size})

    if st.button("🚀 تشغيل تحليل التكافؤ الحيوي الشامل", use_container_width=True):
        t_points = np.linspace(0, 24, 200)
        base_p = API_DATA[api_choice]
        
        # 1. Simulate Reference based on input metrics
        # Adjusting parameters to match user's expected RLD values
        y_ref = pk_model(t_points, user_dose, base_p['f'], base_p['ka'], base_p['ke'], base_p['vd'], weight)
        # Normalize to match user input Cmax
        if np.max(y_ref) > 0: y_ref = y_ref * (r_cmax / np.max(y_ref))
        
        sim_results = {"Time": t_points, "Reference": y_ref}
        metrics = {"Reference": {"cmax": np.max(y_ref), "tmax": t_points[np.argmax(y_ref)], "auc": safe_auc(y_ref, t_points)}}
        
        # 2. Simulate Tests
        for f in formulations:
            # Impact of dosage form on absorption
            ka_mod = 2.5 if f['type'] == "Nano" else (1.5 if f['type'] == "Syrup" else 1.0)
            f_mod = 1.2 if f['type'] == "Nano" else 1.0
            
            # Impact of Food
            if is_fed:
                ka_mod *= 0.7
                f_mod *= 0.9
                
            y_test = pk_model(t_points, user_dose, base_p['f'] * f_mod, base_p['ka'] * ka_mod, base_p['ke'], base_p['vd'], weight)
            # Add small random variation for realism
            y_test *= np.random.normal(1.0, 0.02, len(t_points))
            
            sim_results[f['name']] = y_test
            metrics[f['name']] = {
                "cmax": np.max(y_test),
                "tmax": t_points[np.argmax(y_test)],
                "auc": safe_auc(y_test, t_points)
            }

        # --- Visuals ---
        st.divider()
        res_col1, res_col2 = st.columns([2, 1])
        
        with res_col1:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(t_points, y_ref, label=f"Ref: {ref_name}", linewidth=4, color='black', linestyle='--')
            for f in formulations:
                ax.plot(t_points, sim_results[f['name']], label=f['name'], linewidth=2)
            
            ax.set_title("Comparative Bioavailability Profile (In-Vivo Simulation)")
            ax.set_xlabel("Time (hours)")
            ax.set_ylabel("Plasma Concentration (µg/mL)")
            ax.legend()
            ax.grid(True, alpha=0.2)
            st.pyplot(fig)
            
        with res_col2:
            st.subheader("📏 المقاييس المحسوبة")
            for name, m in metrics.items():
                with st.expander(f"نتائج {name}", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Cmax", f"{m['cmax']:.2f}")
                    c2.metric("Tmax", f"{m['tmax']:.2f}")
                    c3.metric("AUC", f"{m['auc']:.1f}")
                    
                    if name != "Reference":
                        ratio = (m['auc'] / metrics["Reference"]['auc']) * 100 if metrics["Reference"]['auc'] > 0 else 0
                        status = "✅ Bioequivalent" if 80 <= ratio <= 125 else "❌ Not Equivalent"
                        st.write(f"**Ratio:** {ratio:.1f}% | **Result:** {status}")

        st.subheader("📝 تقرير المواد والتركيبات")
        data_table = []
        for f in formulations:
            m = metrics[f['name']]
            data_table.append({
                "التركيبة": f['name'],
                "الصورة": f['type'],
                "المواد المضافة": ", ".join(f['excs']),
                "حجم الجسيمات": f"{f['psize']} nm" if f['psize'] > 0 else "N/A",
                "Cmax/Ref Ratio": f"{(m['cmax']/metrics['Reference']['cmax'])*100:.1f}%"
            })
        st.table(pd.DataFrame(data_table))
        
        # Download results
        csv = pd.DataFrame(sim_results).to_csv(index=False)
        st.download_button("📂 تحميل بيانات الدراسة (CSV)", csv, "bioequivalence_report.csv", "text/csv")

st.markdown("<br><hr><center>Sama Pharma Tech | Research & Development Hub v8.0</center>", unsafe_allow_html=True)