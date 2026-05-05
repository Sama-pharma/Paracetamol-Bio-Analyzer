import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(
    page_title="Sama Pharma Tech | Precision BE Hub",
    page_icon="🧬",
    layout="wide"
)

# --- Enhanced Visual Styling (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .main-header { color: #1e3a8a; text-align: center; font-weight: 800; font-size: 2.5rem; margin-bottom: 20px; border-bottom: 4px solid #2563eb; padding-bottom: 10px; }
    .section-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .reference-section { border: 2px solid #1e3a8a; background-color: #f0f7ff; border-radius: 10px; padding: 15px; margin-top: 10px; }
    .metric-label { color: #64748b; font-size: 0.85rem; font-weight: bold; }
    .metric-value { color: #1e293b; font-size: 1.1rem; font-weight: 800; }
    .error-box { background-color: #fef2f2; border: 1px solid #ef4444; color: #b91c1c; padding: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- Real Pharmacokinetic Profiles ---
PHARMA_DB = {
    "Paracetamol": {"ka": 2.1, "ke": 0.28, "vd": 0.95, "f": 0.88},
    "Atorvastatin": {"ka": 0.8, "ke": 0.05, "vd": 5.4, "f": 0.12},
    "Metformin": {"ka": 1.2, "ke": 0.15, "vd": 1.5, "f": 0.55},
    "Ibuprofen": {"ka": 1.8, "ke": 0.35, "vd": 0.12, "f": 0.92}
}

# --- Mathematical Engines ---
def get_auc(conc, time):
    """Calculates Area Under Curve using Trapezoidal Rule."""
    if len(conc) < 2: return 0.0
    # Safe implementation of trapezoidal rule
    return np.trapz(conc, time)

def generate_pk_curve(t, dose, f, ka, ke, vd, weight):
    """Standard 1-Compartment PK Model (Bateman Equation)."""
    v_total = vd * weight
    # Avoid division by zero if ka == ke
    if abs(ka - ke) < 1e-4: ka += 0.001
    
    pre_factor = (f * dose * ka) / (v_total * (ka - ke))
    conc = pre_factor * (np.exp(-ke * t) - np.exp(-ka * t))
    return np.maximum(0, conc)

def calculate_exact_metrics(dose, f, ka, ke, vd, weight):
    """Calculates Tmax and Cmax analytically for zero-error reference."""
    v_total = vd * weight
    tmax = np.log(ka/ke) / (ka - ke)
    cmax = (f * dose * ka / (v_total * (ka - ke))) * (np.exp(-ke * tmax) - np.exp(-ka * tmax))
    return tmax, cmax

# --- UI Layout ---
st.markdown("<h1 class='main-header'>🧬 Sama Pharma Tech | Precision PK Hub v5.1</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ إعدادات المحاكاة")
    selected_api = st.selectbox("المادة الفعالة", list(PHARMA_DB.keys()))
    drug_params = PHARMA_DB[selected_api]
    
    st.divider()
    dose = st.number_input("الجرعة (mg)", value=500.0)
    weight = st.number_input("وزن الجسم (kg)", value=70.0)
    food_effect = st.checkbox("تأثير الطعام (Fed State)")
    
    st.divider()
    st.info("تستخدم هذه النسخة محركاً رياضياً محدثاً لتجنب أخطاء القسمة على صفر ونقص المكتبات.")

# --- Logic Processing ---
tab1, tab2 = st.tabs(["📊 التحليل والمقارنة", "📋 التقارير"])

with tab1:
    col_input1, col_input2, col_input3 = st.columns(3)
    
    # Simple form inputs for formulas
    with col_input1:
        f1_name = st.text_input("اسم التركيبة 1", "Sama-Nano-01")
        f1_type = st.selectbox("النوع 1", ["أقراص", "نانو", "شراب"], key="t1")
    with col_input2:
        f2_name = st.text_input("اسم التركيبة 2", "Sama-Gen-02")
        f2_type = st.selectbox("النوع 2", ["أقراص", "كبسولات", "معلق"], key="t2")
    with col_input3:
        f3_name = st.text_input("اسم التركيبة 3", "Sama-Ref-Test")
        f3_type = st.selectbox("النوع 3", ["أقراص", "ممتدة المفعول"], key="t3")

    if st.button("🚀 تشغيل تحليل التكافؤ الحيوي الشامل", use_container_width=True):
        t_points = np.linspace(0, 24, 200)
        
        # Reference Calculations (Fixed accuracy)
        f_ref = drug_params['f'] * (1.1 if food_effect else 1.0)
        ka_ref = drug_params['ka'] * (0.7 if food_effect else 1.0)
        
        ref_conc = generate_pk_curve(t_points, dose, f_ref, ka_ref, drug_params['ke'], drug_params['vd'], weight)
        tmax_ref, cmax_ref = calculate_exact_metrics(dose, f_ref, ka_ref, drug_params['ke'], drug_params['vd'], weight)
        auc_ref = get_auc(ref_conc, t_points)
        
        # Save to state
        st.session_state.results_df = pd.DataFrame({'Time': t_points, 'Reference (RLD)': ref_conc})
        st.session_state.metrics = {
            'Reference (RLD)': {'cmax': cmax_ref, 'tmax': tmax_ref, 'auc': auc_ref}
        }
        
        # Test Formulations
        configs = [
            (f1_name, 1.15 if f1_type == "نانو" else 1.0, 1.5 if f1_type == "نانو" else 1.0),
            (f2_name, 0.95, 0.9),
            (f3_name, 0.85 if "ممتدة" in f3_type else 1.0, 0.5 if "ممتدة" in f3_type else 1.0)
        ]
        
        for name, f_mod, ka_mod in configs:
            t_conc = generate_pk_curve(t_points, dose, f_ref * f_mod, ka_ref * ka_mod, drug_params['ke'], drug_params['vd'], weight)
            # Add some biological variability
            t_conc *= np.random.normal(1, 0.02, len(t_points))
            st.session_state.results_df[name] = np.maximum(0, t_conc)
            
            st.session_state.metrics[name] = {
                'cmax': t_conc.max(),
                'tmax': t_points[np.argmax(t_conc)],
                'auc': get_auc(t_conc, t_points)
            }
        
        st.success("✅ تمت المعالجة بنجاح!")

    # Display Results if they exist
    if "results_df" in st.session_state:
        df = st.session_state.results_df
        metrics = st.session_state.metrics
        ref_auc = metrics['Reference (RLD)']['auc']
        
        c_plot, c_metrics = st.columns([2, 1])
        
        with c_plot:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(10, 5))
            for col in df.columns[1:]:
                lw = 3 if "Reference" in col else 1.5
                ax.plot(df['Time'], df[col], label=col, linewidth=lw)
            ax.set_title(f"PK Comparison: {selected_api}")
            ax.set_xlabel("Time (h)"); ax.set_ylabel("Plasma Conc. (mg/L)")
            ax.legend(); ax.grid(alpha=0.3)
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c_metrics:
            st.markdown("### 🎯 المخطط المرجعي (RLD)")
            m_ref = metrics['Reference (RLD)']
            st.markdown(f"""
            <div class='reference-section'>
                <p><b>Cmax:</b> {m_ref['cmax']:.2f} mg/L</p>
                <p><b>Tmax:</b> {m_ref['tmax']:.2f} h</p>
                <p><b>AUC:</b> {m_ref['auc']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            st.markdown("### ⚖️ مقارنة التكافؤ (T/R Ratio)")
            for name in list(metrics.keys())[1:]:
                m = metrics[name]
                # CRITICAL: Division Check to prevent ZeroDivisionError
                ratio = (m['auc'] / ref_auc * 100) if ref_auc > 0 else 0
                st.write(f"**{name}**")
                st.progress(min(ratio/150, 1.0))
                st.caption(f"Relative AUC: {ratio:.1f}%")

with tab2:
    if "results_df" in st.session_state:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("📋 تقرير النتائج التفصيلي")
        report_data = []
        for name, m in st.session_state.metrics.items():
            report_data.append({
                "التركيبة": name,
                "Cmax (mg/L)": f"{m['cmax']:.2f}",
                "Tmax (h)": f"{m['tmax']:.2f}",
                "AUC 0-24": f"{m['auc']:.2f}"
            })
        st.table(pd.DataFrame(report_data))
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("الرجاء تشغيل التحليل أولاً لتوليد التقارير.")

st.caption("Precision Bio-Analysis Engine v5.1 | R&D Division")