import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(
    page_title="Sama Pharma Tech | Regulatory Bio-Analyzer",
    page_icon="🧪",
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-header { color: #1A237E; font-weight: bold; text-align: center; font-size: 2.5rem; margin-bottom: 0; }
    .sub-header { text-align: center; color: #555; margin-bottom: 20px; font-style: italic; }
    .stButton>button { background-color: #1A237E; color: white; border-radius: 8px; font-weight: bold; height: 3em; }
    .status-passed { padding: 20px; border-radius: 10px; background-color: #C8E6C9; border-left: 10px solid #2E7D32; color: #1B5E20; font-weight: bold; }
    .status-failed { padding: 20px; border-radius: 10px; background-color: #FFCDD2; border-left: 10px solid #C62828; color: #B71C1C; font-weight: bold; }
    .info-card { padding: 15px; border-radius: 10px; background-color: #ffffff; border: 1px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🔬 Sama Pharma Tech | Bio-equivalence Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>محاكي حركية دوائية حقيقي يعتمد على نماذج رياضية (Pharmacokinetic Modeling)</p>", unsafe_allow_html=True)

st.divider()

if 'df_data' not in st.session_state:
    st.session_state.df_data = None

# --- Real Pharmacokinetic Engine (One-Compartment Model) ---
def calculate_concentration(t, dose, F, Vd, ka, ke):
    # معادلة التركيز: C(t) = [F * Dose * ka / (Vd * (ka - ke))] * (exp(-ke * t) - exp(-ka * t))
    if ka == ke: ka = ke + 0.001  # تجنب القسمة على صفر
    coeff = (F * dose * ka) / (Vd * (ka - ke))
    return coeff * (np.exp(-ke * t) - np.exp(-ka * t))

def simulate_be_data(dosage_form, dose, weight, subject_type, fasting_state):
    time = np.array([0, 0.25, 0.5, 1, 1.5, 2, 4, 8, 12, 18, 24])
    
    # 1. إعداد المعاملات الحيوية بناءً على نوع الكائن (Pharmacokinetics parameters per species)
    if "Human" in subject_type:
        ke = 0.1  # t1/2 ≈ 7h
        Vd_kg = 0.6 # L/kg
    elif "Rat" in subject_type:
        ke = 0.5  # t1/2 ≈ 1.4h (أسرع بكثير)
        Vd_kg = 0.8
    elif "Rabbit" in subject_type:
        ke = 0.3
        Vd_kg = 0.7
    else: # Dogs
        ke = 0.15
        Vd_kg = 0.6
    
    Vd_total = Vd_kg * weight
    F_ref = 0.7 if fasting_state == "Fasted (صائم)" else 0.5 # التوافر الحيوي يتأثر بالأكل
    
    # 2. تحديد خصائص التركيبة (Formulation characteristics)
    ka_ref = 1.2 # ثابت امتصاص قياسي للمرجع
    
    if dosage_form == "Nano-Carrier":
        ka_test = 2.5 # امتصاص أسرع جداً للنانو
        F_test = F_ref * 1.3 # التوافر الحيوي أعلى للنانو
        variability = 0.05
    elif dosage_form == "Oral Suspension":
        ka_test = 1.8
        F_test = F_ref * 1.1
        variability = 0.08
    else: # Conventional
        ka_test = 1.1
        F_test = F_ref * 0.95
        variability = 0.15

    # 3. حساب المنحنيات بناءً على المعادلات الرياضية
    ref_conc = [calculate_concentration(t, dose, F_ref, Vd_total, ka_ref, ke) for t in time]
    test_conc = [calculate_concentration(t, dose, F_test, Vd_total, ka_test, ke) for t in time]

    # إضافة تشتت بيولوجي واقعي (Inter-subject variability)
    ref_final = np.array(ref_conc) * np.random.normal(1, variability, len(time))
    test_final = np.array(test_conc) * np.random.normal(1, variability, len(time))
    
    st.session_state.df_data = pd.DataFrame({
        'Time': time,
        'Reference': np.maximum(np.round(ref_final, 3), 0),
        'Test': np.maximum(np.round(test_final, 3), 0)
    })

# --- Sidebar: Input Parameters ---
with st.sidebar:
    st.header("📋 بروتوكول الدراسة")
    study_id = st.text_input("رقم الدراسة", "SPT-PK-2024-MATH")
    drug_api = st.text_input("المادة الفعالة (API)", "Atorvastatin")
    
    col_drugs = st.columns(2)
    with col_drugs[0]:
        test_brand = st.text_input("الدواء المختبر", "Sama-Nano")
    with col_drugs[1]:
        ref_brand = st.text_input("الدواء المرجعي", "Lipitor")

    st.divider()
    
    st.header("🐾 المدخلات البيولوجية")
    subject_type = st.selectbox("نوع الكائن", ["Human (بشر)", "Rat (جرذان)", "Rabbit (أرانب)", "Beagle Dog (كلاب)"])
    avg_weight = st.number_input("الوزن (kg)", value=70.0 if "Human" in subject_type else 0.25, step=0.1)
    subject_count = st.slider("عدد العينة (N)", 6, 48, 12)
    
    st.divider()
    
    st.header("💊 الجرعة والظروف")
    dose_value = st.number_input("الجرعة الكلية (mg)", value=20.0, step=1.0)
    fasting_state = st.radio("حالة التغذية", ["Fasted (صائم)", "Fed (بعد الأكل)"])

    st.divider()
    
    st.header("🧪 تكنولوجيا التصنيع")
    dosage_form = st.selectbox("نظام التوصيل", ["Nano-Carrier", "Conventional Tablet", "Oral Suspension"])
    
    st.divider()
    
    if st.button("🚀 تشغيل المحاكاة الرياضية"): 
        simulate_be_data(dosage_form, dose_value, avg_weight, subject_type, fasting_state)

# --- Analysis Engine ---
def get_regulatory_analysis(df, n_subjects):
    results = {}
    for col in ['Reference', 'Test']:
        conc = df[col].values
        time = df['Time'].values
        cmax = np.max(conc)
        tmax = time[np.argmax(conc)]
        
        try:
            auc = np.trapezoid(conc, time)
        except AttributeError:
            auc = np.trapz(conc, time)
        
        # تشتت العينة الحقيقي
        cv = (np.std(conc)/np.mean(conc)) if np.mean(conc) > 0 else 0.1
        results[col] = {'Cmax': cmax, 'Tmax': tmax, 'AUC': auc, 'CV': cv * 100}
    
    auc_ratio = (results['Test']['AUC'] / results['Reference']['AUC'])
    cmax_ratio = (results['Test']['Cmax'] / results['Reference']['Cmax'])
    
    # فاصل الثقة الإحصائي
    sd_pooled = np.sqrt((results['Test']['CV']**2 + results['Reference']['CV']**2) / 2) / 100
    error_margin = 1.645 * (sd_pooled / np.sqrt(n_subjects)) 
    
    ci_low = np.exp(np.log(auc_ratio) - error_margin) * 100
    ci_high = np.exp(np.log(auc_ratio) + error_margin) * 100
    
    return results, (auc_ratio*100, cmax_ratio*100), (ci_low, ci_high)

# --- Display Results ---
if st.session_state.df_data is not None:
    df = st.session_state.df_data
    stats_res, ratios, ci = get_regulatory_analysis(df, subject_count)
    
    st.markdown(f"""
    <div class='info-card'>
        <div style="display: flex; justify-content: space-between;">
            <div><strong>Study:</strong> {study_id} | <strong>API:</strong> {drug_api}</div>
            <div><strong>Species:</strong> {subject_type} ({avg_weight}kg)</div>
            <div><strong>Dose:</strong> {dose_value}mg</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2 = st.columns([2, 1])

    with m1:
        st.subheader("📈 PK Profile (Mathematical Model)")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df['Time'], df['Reference'], 's--', label=f"Ref: {ref_brand}", color="#D32F2F", alpha=0.7)
        ax.plot(df['Time'], df['Test'], 'o-', label=f"Test: {test_brand}", color="#1A237E", linewidth=2.5)
        ax.set_xlabel("Time (Hours)")
        ax.set_ylabel("Plasma Conc (mg/L)")
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend()
        st.pyplot(fig)

    with m2:
        st.subheader("📋 Calculated PK Metrics")
        for key, name in [('Reference', ref_brand), ('Test', test_brand)]:
            with st.expander(f"Metrics for {name}", expanded=True):
                d = stats_res[key]
                st.write(f"**Cmax:** {d['Cmax']:.3f} mg/L")
                st.write(f"**Tmax:** {d['Tmax']:.2f} h")
                st.write(f"**AUC₀₋₂₄:** {d['AUC']:.3f} mg*h/L")

    st.divider()
    st.subheader("⚖️ Statistical Bioequivalence Analysis")
    c1, c2, c3 = st.columns(3)
    c1.metric("AUC Ratio (T/R)", f"{ratios[0]:.2f}%")
    c2.metric("Cmax Ratio (T/R)", f"{ratios[1]:.2f}%")
    c3.metric("90% CI (Accepted: 80-125%)", f"{ci[0]:.2f}% - {ci[1]:.2f}%")

    is_be = (80 <= ci[0] <= 125) and (80 <= ci[1] <= 125)
    if is_be:
        st.markdown(f"<div class='status-passed'>✅ PASSED: The products are bioequivalent based on the PK model.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='status-failed'>❌ FAILED: Significant difference detected in absorption/exposure.</div>", unsafe_allow_html=True)
else:
    st.info("قم بإدخال بيانات البروتوكول واضغط على 'تشغيل المحاكاة الرياضية' لإنشاء نتائج تعتمد على معادلات الحركية الدوائية.")