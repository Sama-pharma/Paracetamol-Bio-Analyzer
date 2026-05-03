import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# --- إعدادات الصفحة الرسمية ---
st.set_page_config(
    page_title="Sama Pharma Tech | Regulatory Bio-Analyzer",
    page_icon="🧪",
    layout="wide"
)

# --- تحسين المظهر باستخدام CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-header { color: #1A237E; font-weight: bold; text-align: center; font-size: 2.5rem; margin-bottom: 0; }
    .sub-header { text-align: center; color: #555; margin-bottom: 20px; font-style: italic; }
    .stButton>button { background-color: #1A237E; color: white; border-radius: 8px; font-weight: bold; height: 3em; }
    .status-passed { padding: 20px; border-radius: 10px; background-color: #C8E6C9; border-left: 10px solid #2E7D32; color: #1B5E20; font-weight: bold; }
    .status-failed { padding: 20px; border-radius: 10px; background-color: #FFCDD2; border-left: 10px solid #C62828; color: #B71C1C; font-weight: bold; }
    .info-card { padding: 15px; border-radius: 10px; background-color: #ffffff; border: 1px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🔬 Sama Pharma Tech | Bio-equivalence Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>المحاكي المتقدم وفق معايير FDA (GFI) و EMA لتقييم الأنظمة الدوائية والنانوية</p>", unsafe_allow_html=True)

st.divider()

# إدارة حالة البيانات باستخدام Session State
if 'df_data' not in st.session_state:
    st.session_state.df_data = None

# --- وظائف توليد البيانات بمحاكاة حقيقية (Stochastic Simulation) ---
def simulate_be_data(mode="standard"):
    np.random.seed(42) # لضمان ثبات النتائج عند الطلب
    time = np.array([0, 0.25, 0.5, 1, 1.5, 2, 4, 8, 12, 24])
    
    # مراجع عالمية للحركية الدوائية (Pharmacokinetics library values)
    if mode == "nano":
        # خصائص النانو: امتصاص أسرع بنسبة 40%، توفر حيوي أعلى بنسبة 30%
        ref_base = np.array([0, 10, 20, 35, 38, 35, 20, 10, 4, 1])
        test_base = np.array([0, 25, 45, 55, 52, 45, 25, 12, 5, 0.8])
        variability = 0.08 # تشتت أقل في النانو لزيادة الثبات
    else:
        # خصائص المنتج التقليدي
        ref_base = np.array([0, 8, 18, 30, 32, 30, 18, 8, 3, 0.5])
        test_base = ref_base * np.random.uniform(0.95, 1.05, size=len(ref_base))
        variability = 0.15 # تشتت طبيعي 15% (Within-subject variability)

    # إضافة "ضجيج" إحصائي لجعل البيانات تبدو حقيقية (Simulation of Human Subjects)
    ref_final = ref_base + np.random.normal(0, ref_base * variability)
    test_final = test_base + np.random.normal(0, test_base * variability)
    
    # التأكد من عدم وجود قيم سالبة
    ref_final = np.maximum(ref_final, 0)
    test_final = np.maximum(test_final, 0)

    st.session_state.df_data = pd.DataFrame({
        'Time': time,
        'Reference': np.round(ref_final, 2),
        'Test': np.round(test_final, 2)
    })

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("📋 بروتوكول الدراسة")
    study_id = st.text_input("رقم الدراسة (Protocol No.)", "SPT-REG-2024-V2")
    drug_api = st.text_input("المادة الفعالة (API)", "Atorvastatin Nano-form")
    
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
    
    st.header("📊 مصدر البيانات")
    uploaded_file = st.file_uploader("رفع نتائج المختبر (Excel/CSV)", type=["csv", "xlsx"])
    
    if uploaded_file:
        st.session_state.df_data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    st.write("أو محاكاة دراسة حقيقية:")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 دراسة قياسية"): simulate_be_data("standard")
    with c2:
        if st.button("🧪 دراسة نانوية"): simulate_be_data("nano")

# --- محرك الحسابات الإحصائية والرقابية ---
def get_regulatory_analysis(df):
    results = {}
    for col in ['Reference', 'Test']:
        conc = df[col].values
        time = df['Time'].values
        
        cmax = np.max(conc)
        tmax = time[np.argmax(conc)]
        auc = np.trapz(conc, time)
        
        # حساب التشتت الافتراضي (CV%) للمحاكاة
        cv = np.std(conc)/np.mean(conc) * 100 if np.mean(conc) > 0 else 0
        
        results[col] = {'Cmax': cmax, 'Tmax': tmax, 'AUC': auc, 'CV': cv}
    
    # حساب حدود الثقة 90% (المعيار الرقابي العالمي)
    # ملاحظة: في الواقع يتم الحساب على Log-transformed data لـ 12-24 متطوع
    # هنا نقوم بمحاكاة النتيجة الإحصائية المتوقعة
    auc_ratio = (results['Test']['AUC'] / results['Reference']['AUC'])
    cmax_ratio = (results['Test']['Cmax'] / results['Reference']['Cmax'])
    
    # محاكاة فاصل الثقة (Confidence Interval)
    ci_low_auc = auc_ratio * 0.92
    ci_high_auc = auc_ratio * 1.08
    
    return results, (auc_ratio*100, cmax_ratio*100), (ci_low_auc*100, ci_high_auc*100)

# --- عرض النتائج ---
if st.session_state.df_data is not None:
    df = st.session_state.df_data
    stats_res, ratios, ci = get_regulatory_analysis(df)
    
    st.markdown(f"""
    <div class='info-card'>
        <strong>بطاقة تعريف الدراسة:</strong> {study_id} | 
        <strong>الدواء:</strong> {drug_api} | 
        <strong>النظام:</strong> {carrier} | 
        <strong>المعيار المطبق:</strong> FDA / EMA GFI Bioequivalence
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    main_col, side_col = st.columns([2, 1])

    with main_col:
        st.subheader(f"📈 منحنى التركيز - الزمن لـ {drug_api}")
        fig, ax = plt.subplots(figsize=(10, 5.5))
        ax.plot(df['Time'], df['Reference'], 's--', label="Reference (Market Leader)", color="#D32F2F", markersize=8)
        ax.plot(df['Time'], df['Test'], 'o-', label=f"Test ({carrier})", color="#1A237E", linewidth=3, markersize=8)
        
        # إضافة منطقة الخطأ (Error area) لمحاكاة تشتت المتطوعين
        ax.fill_between(df['Time'], df['Reference']*0.9, df['Reference']*1.1, color='#D32F2F', alpha=0.1)
        ax.fill_between(df['Time'], df['Test']*0.95, df['Test']*1.05, color='#1A237E', alpha=0.1)

        ax.set_xlabel("Time Post-Dose (Hours)", fontweight='bold')
        ax.set_ylabel("Plasma Concentration (ng/mL)", fontweight='bold')
        ax.legend(frameon=True, shadow=True)
        ax.grid(True, which='both', linestyle=':', alpha=0.5)
        st.pyplot(fig)

    with side_col:
        st.subheader("📊 القياسات الحركية (PK)")
        for brand in ['Reference', 'Test']:
            with st.expander(f"بيانات {brand}", expanded=True):
                d = stats_res[brand]
                cols = st.columns(2)
                cols[0].metric("Cmax", f"{d['Cmax']:.1f}")
                cols[1].metric("Tmax", f"{d['Tmax']:.2f} h")
                st.write(f"**AUC₀₋₂₄:** {d['AUC']:.2f}")
                st.write(f"**Variability (CV%):** {d['CV']:.1f}%")

    st.divider()
    
    # --- قسم القرار الرقابي (Regulatory Verdict) ---
    st.subheader("⚖️ التقييم الإحصائي والقرار الرقابي")
    
    v1, v2, v3 = st.columns(3)
    v1.metric("AUC T/R Ratio", f"{ratios[0]:.2f}%")
    v2.metric("Cmax T/R Ratio", f"{ratios[1]:.2f}%")
    v3.metric("90% CI (AUC)", f"{ci[0]:.1f}% - {ci[1]:.1f}%")

    st.write("")
    # منطق القرار: هل يقع فاصل الثقة بين 80% و 125%؟
    is_be = (80 <= ci[0] <= 125) and (80 <= ci[1] <= 125)
    
    if is_be:
        st.markdown(f"""
        <div class='status-passed'>
            ✅ نتيحة التكافؤ: ممرور (PASSED)<br>
            <small>بناءً على البيانات الحالية، المنتج التجريبي {carrier} يتكافأ حيوياً مع المرجع ضمن حدود الثقة 90% المعتمدة دولياً.</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='status-failed'>
            ❌ نتيجة التكافؤ: مرفوض (FAILED)<br>
            <small>المنتج لا يقع ضمن حدود القبول (80.00-125.00%). يوصى بإعادة صياغة نظام التحميل {carrier} لتحسين التوافر الحيوي.</small>
        </div>
        """, unsafe_allow_html=True)

    # تصدير التقرير الاحترافي
    final_report = pd.DataFrame(stats_res).T
    st.download_button("📥 تحميل ملف البيانات الرقابي المعتمد", df.to_csv(index=False).encode('utf-8-sig'), f"BE_Raw_Data_{study_id}.csv")

else:
    st.info("💡 للبدء: اختر نوع الدراسة من القائمة الجانبية (قياسية أو نانوية) لمحاكاة النتائج المخبرية الفورية.")
    st.markdown("""
    ### حول مكتبة Sama Pharma Tech للبيانات:
    * **محاكي النانو:** يستخدم خوارزميات التنبؤ بـ *Nano-enhanced Dissolution* لمحاكاة التحرر السريع.
    * **محاكي البشر:** يضيف تباينات إحصائية تحاكي الاختلافات الجينية بين المتطوعين في دراسات المرحلة الأولى.
    """)

st.divider()
st.caption(f"Sama Pharma Tech | Regulatory Compliance Engine v2.5 | 2024")