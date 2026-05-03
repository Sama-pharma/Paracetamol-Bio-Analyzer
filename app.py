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
st.markdown("<p class='sub-header'>المحاكي المتقدم وفق معايير FDA (GFI) و EMA لتقييم الأنظمة الدوائية والنانوية</p>", unsafe_allow_html=True)

st.divider()

if 'df_data' not in st.session_state:
    st.session_state.df_data = None

# --- Dynamic Simulation Engine ---
def simulate_be_data(mode, dose, weight, subject_type):
    # إزالة التثبيت العشوائي لجعل النتائج حيوية
    time = np.array([0, 0.25, 0.5, 1, 1.5, 2, 4, 8, 12, 24])
    
    # معامل تعديل بناءً على الوزن والجرعة (Dose/Weight scaling)
    # نفترض أن التركيز يتناسب طردياً مع الجرعة وعكسياً مع الوزن
    base_scalar = (dose / weight) * 10
    
    # تعديل المعاملات بناءً على نوع الكائن (Pharmacokinetic scaling)
    species_factor = 1.0
    if "Rat" in subject_type: species_factor = 0.5 # استقلاب أسرع
    elif "Rabbit" in subject_type: species_factor = 0.8
    
    if mode == "nano":
        # خصائص النانو: Ka أعلى (امتصاص أسرع) و Ke أقل (استقرار)
        ref_base = np.array([0, 8, 15, 25, 28, 25, 15, 8, 3, 0.5]) * base_scalar * species_factor
        test_base = np.array([0, 15, 30, 45, 42, 35, 20, 10, 4, 0.6]) * base_scalar * species_factor
        variability = 0.04 # النانو عادة أكثر تجانساً
    else:
        # خصائص المنتج التقليدي
        ref_base = np.array([0, 8, 18, 30, 32, 30, 18, 8, 3, 0.5]) * base_scalar * species_factor
        # تذبذب عشوائي حقيقي للتجربة التقليدية
        test_base = ref_base * np.random.uniform(0.85, 1.15, size=len(ref_base))
        variability = 0.12 

    # إضافة الضجيج البيولوجي (Biological Noise)
    ref_final = ref_base + np.random.normal(0, ref_base * variability)
    test_final = test_base + np.random.normal(0, test_base * variability)
    
    ref_final = np.maximum(ref_final, 0)
    test_final = np.maximum(test_final, 0)

    st.session_state.df_data = pd.DataFrame({
        'Time': time,
        'Reference': np.round(ref_final, 2),
        'Test': np.round(test_final, 2)
    })

# --- Sidebar: Input Parameters ---
with st.sidebar:
    st.header("📋 بروتوكول الدراسة")
    study_id = st.text_input("رقم الدراسة (Protocol No.)", "SPT-REG-2024-V2")
    drug_api = st.text_input("المادة الفعالة (API)", "Atorvastatin")
    
    st.divider()
    
    st.header("🐾 بيانات الكائن الحي")
    subject_type = st.selectbox("نوع الكائن", ["Human (بشر)", "Rat (جرذان)", "Rabbit (أرانب)", "Beagle Dog (كلاب)"])
    avg_weight = st.number_input("متوسط الوزن (kg)", value=70.0 if "Human" in subject_type else 0.25, step=0.1)
    subject_count = st.slider("عدد العينة (N)", 6, 48, 12)
    
    st.divider()
    
    st.header("💊 تفاصيل الجرعة")
    dose_value = st.number_input("الجرعة (mg)", value=20.0, step=1.0)
    admin_route = st.selectbox("طريقة الإعطاء", ["Oral (فموي)", "IV (وريدي)", "Subcutaneous"])
    fasting_state = st.radio("حالة التغذية", ["Fasted (صائم)", "Fed (بعد الأكل)"])

    st.divider()
    
    st.header("🧪 التصميم الصيدلاني")
    dosage_form = st.selectbox("النظام التوصيلي", ["Nano-Carrier", "Conventional Tablet", "Oral Suspension"])
    
    carriers_dict = {
        "Nano-Carrier": ["Solid Lipid Nanoparticles", "Nano-emulsion", "Liposomes"],
        "Conventional Tablet": ["Lactose-Based", "MCC-Starch", "Povidone-Matrix"],
        "Oral Suspension": ["Xanthan Gum", "CMC-Na", "Sorbitol Solution"]
    }
    carrier = st.selectbox("مادة التحميل المستخدمة", carriers_dict[dosage_form])

    st.divider()
    
    st.write("تشغيل المحاكاة بناءً على المدخلات:")
    if st.button("🚀 بدء تحليل المحاكاة"): 
        mode = "nano" if dosage_form == "Nano-Carrier" else "standard"
        simulate_be_data(mode, dose_value, avg_weight, subject_type)

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
        
        cv = np.std(conc)/np.mean(conc) if np.mean(conc) > 0 else 0
        results[col] = {'Cmax': cmax, 'Tmax': tmax, 'AUC': auc, 'CV': cv * 100}
    
    auc_ratio = (results['Test']['AUC'] / results['Reference']['AUC'])
    cmax_ratio = (results['Test']['Cmax'] / results['Reference']['Cmax'])
    
    # Enhanced Statistical CI calculation
    sd_pooled = np.sqrt((results['Test']['CV']**2 + results['Reference']['CV']**2) / 2) / 100
    error_margin = 1.645 * (sd_pooled / np.sqrt(n_subjects)) 
    
    ci_low_auc = np.exp(np.log(auc_ratio) - error_margin)
    ci_high_auc = np.exp(np.log(auc_ratio) + error_margin)
    
    return results, (auc_ratio*100, cmax_ratio*100), (ci_low_auc*100, ci_high_auc*100)

# --- Display Results ---
if st.session_state.df_data is not None:
    df = st.session_state.df_data
    stats_res, ratios, ci = get_regulatory_analysis(df, subject_count)
    
    st.markdown(f"""
    <div class='info-card'>
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
            <div><strong>Study:</strong> {study_id}</div>
            <div><strong>Drug:</strong> {drug_api}</div>
            <div><strong>Subject:</strong> {subject_type} ({avg_weight}kg)</div>
            <div><strong>Dose:</strong> {dose_value}mg</div>
            <div><strong>Formulation:</strong> {carrier}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2 = st.columns([2, 1])

    with m1:
        st.subheader("📊 Pharmacokinetic Profile")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df['Time'], df['Reference'], 's--', label="Reference", color="#D32F2F")
        ax.plot(df['Time'], df['Test'], 'o-', label=f"Test ({carrier})", color="#1A237E", linewidth=2)
        ax.set_xlabel("Time (h)")
        ax.set_ylabel("Conc (ng/mL)")
        ax.legend()
        st.pyplot(fig)

    with m2:
        st.subheader("📋 PK Metrics")
        for b in ['Reference', 'Test']:
            with st.expander(f"{b} Results"):
                st.write(f"Cmax: {stats_res[b]['Cmax']:.2f}")
                st.write(f"Tmax: {stats_res[b]['Tmax']:.2f} h")
                st.write(f"AUC: {stats_res[b]['AUC']:.2f}")

    st.divider()
    st.subheader("⚖️ Bioequivalence Decision")
    c1, c2, c3 = st.columns(3)
    c1.metric("AUC Ratio", f"{ratios[0]:.2f}%")
    c2.metric("Cmax Ratio", f"{ratios[1]:.2f}%")
    c3.metric("90% CI", f"{ci[0]:.2f}% - {ci[1]:.2f}%")

    is_be = (80 <= ci[0] <= 125) and (80 <= ci[1] <= 125)
    if is_be:
        st.markdown("<div class='status-passed'>✅ PASSED: Products are Bioequivalent</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-failed'>❌ FAILED: Products are NOT Bioequivalent</div>", unsafe_allow_html=True)
else:
    st.info("قم بتعديل البيانات في القائمة الجانبية ثم اضغط على 'بدء تحليل المحاكاة' لرؤية النتائج المتغيرة.")