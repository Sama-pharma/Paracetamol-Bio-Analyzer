import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- إعداد الصفحة ---
st.set_page_config(
    page_title="Sama Pharma Tech | Bio-Equivalence Hub",
    page_icon="🧬",
    layout="wide"
)

# --- تنسيقات واجهة المستخدم (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .main-header { color: #1e3a8a; text-align: center; font-weight: 800; font-size: 2.2rem; margin-bottom: 25px; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .ref-box { background-color: #eff6ff; border-right: 5px solid #2563eb; padding: 15px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- المحرك الرياضي (بدون مكتبات خارجية معقدة لضمان التوافق) ---

def calculate_auc_safe(y, x):
    """
    حساب المساحة تحت المنحنى بطريقة شبه المنحرف يدوياً
    لضمان التوافق مع إصدارات Numpy الجديدة التي حذفت np.trapz
    """
    if len(y) != len(x) or len(y) < 2:
        return 0.0
    
    auc = 0.0
    for i in range(len(x) - 1):
        # المساحة = القاعدة المتوسطة × الارتفاع
        h = x[i+1] - x[i]
        avg_y = (y[i] + y[i+1]) / 2.0
        auc += h * avg_y
    return auc

def get_pk_concentration(t, dose, f, ka, ke, vd, weight):
    """Bateman Equation: معادلة الحركية الدوائية للجرعة الفموية"""
    v_dist = vd * weight
    # الحماية من القسمة على صفر في حال تساوي ka و ke
    if abs(ka - ke) < 1e-5:
        ka += 0.001
        
    coefficient = (f * dose * ka) / (v_dist * (ka - ke))
    conc = coefficient * (np.exp(-ke * t) - np.exp(-ka * t))
    return np.maximum(0, conc)

# --- قاعدة بيانات المواد الفعالة ---
DRUG_DATA = {
    "Paracetamol": {"ka": 2.2, "ke": 0.28, "vd": 0.95, "f": 0.85},
    "Atorvastatin": {"ka": 0.7, "ke": 0.05, "vd": 5.0, "f": 0.12},
    "Ibuprofen": {"ka": 1.8, "ke": 0.35, "vd": 0.12, "f": 0.90},
    "Metformin": {"ka": 1.1, "ke": 0.15, "vd": 1.6, "f": 0.50}
}

# --- واجهة المستخدم الرئيسية ---
st.markdown("<h1 class='main-header'>🧬 Sama Pharma Tech | Precision Bio-Analyzer v6.0</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🧪 بارامترات الدراسة")
    drug_choice = st.selectbox("اختر المادة الفعالة", list(DRUG_DATA.keys()))
    params = DRUG_DATA[drug_choice]
    
    st.divider()
    dose_mg = st.number_input("الجرعة (mg)", value=500.0, step=50.0)
    weight_kg = st.number_input("وزن المتطوع (kg)", value=70.0, step=1.0)
    food_state = st.radio("حالة التغذية", ["صائم (Fasted)", "بعد الطعام (Fed)"])
    
    st.divider()
    st.info("تم تحديث النظام ليعمل بشكل مستقل عن مكتبة Scipy ولحل مشكلات إصدارات Numpy الجديدة.")

# --- المعالجة والمنطق ---
t_points = np.linspace(0, 24, 250)

# 1. حساب بيانات المرجع (Reference RLD)
f_val = params['f'] * (0.85 if food_state == "بعد الطعام (Fed)" else 1.0)
ka_val = params['ka'] * (0.6 if food_state == "بعد الطعام (Fed)" else 1.0)

ref_conc = get_pk_concentration(t_points, dose_mg, f_val, ka_val, params['ke'], params['vd'], weight_kg)
auc_ref = calculate_auc_safe(ref_conc, t_points)
cmax_ref = np.max(ref_conc)
tmax_ref = t_points[np.argmax(ref_conc)]

# 2. واجهة الإدخال للتركيبات الجديدة
col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    name1 = st.text_input("التركيبة 1", "Sama-Nano-01")
    tech1 = st.selectbox("التقنية 1", ["أقراص عادية", "تقنية النانو", "محلول"])
with col_t2:
    name2 = st.text_input("التركيبة 2", "Sama-Generic-02")
    tech2 = st.selectbox("التقنية 2", ["أقراص عادية", "كبسولات", "ممتد المفعول"])
with col_t3:
    name3 = st.text_input("التركيبة 3", "Sama-Ref-Test")
    tech3 = st.selectbox("التقنية 3", ["أقراص عادية", "مضغ"])

if st.button("🚀 تشغيل تحليل التكافؤ الحيوي والنتائج"):
    # حساب بيانات الاختبار
    test_configs = [
        (name1, 1.15 if tech1 == "تقنية النانو" else 1.0, 1.4 if tech1 == "تقنية النانو" else 1.0),
        (name2, 0.98, 0.95),
        (name3, 0.88, 0.75)
    ]
    
    results = {"Time": t_points, "Reference (RLD)": ref_conc}
    metrics = {"Reference (RLD)": {"cmax": cmax_ref, "tmax": tmax_ref, "auc": auc_ref}}
    
    for t_name, f_mod, ka_mod in test_configs:
        t_conc = get_pk_concentration(t_points, dose_mg, f_val * f_mod, ka_val * ka_mod, params['ke'], params['vd'], weight_kg)
        # إضافة تباين حيوي بسيط (Biovariability) لجعل النتائج واقعية
        t_conc = t_conc * (1 + np.random.normal(0, 0.01, len(t_points)))
        results[t_name] = t_conc
        metrics[t_name] = {
            "cmax": np.max(t_conc),
            "tmax": t_points[np.argmax(t_conc)],
            "auc": calculate_auc_safe(t_conc, t_points)
        }
        
    st.session_state['study_data'] = pd.DataFrame(results)
    st.session_state['study_metrics'] = metrics
    st.success("تم تحديث النتائج بدقة فيزيولوجية عالية.")

# --- عرض النتائج ---
if 'study_data' in st.session_state:
    df = st.session_state['study_data']
    mets = st.session_state['study_metrics']
    
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("📈 منحنيات التركيز (PK Profiles)")
        fig, ax = plt.subplots(figsize=(10, 5))
        for col in df.columns[1:]:
            width = 3.5 if "Reference" in col else 1.8
            style = '--' if "Reference" in col else '-'
            ax.plot(df['Time'], df[col], label=col, linewidth=width, linestyle=style)
        
        ax.set_xlabel("Time (hours)")
        ax.set_ylabel("Concentration (mg/L)")
        ax.grid(True, which='both', linestyle=':', alpha=0.5)
        ax.legend()
        st.pyplot(fig)
        
    with c_right:
        st.subheader("🎯 المقياس المرجعي")
        m_ref = mets["Reference (RLD)"]
        st.markdown(f"""
        <div class='ref-box'>
            <b>Innovator Reference:</b><br>
            Cmax: {m_ref['cmax']:.2f} mg/L<br>
            Tmax: {m_ref['tmax']:.2f} h<br>
            AUC: {m_ref['auc']:.2f}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("⚖️ نسب التكافؤ (Ratio %)")
        
        # حماية من القسمة على صفر في حالة لم يتم حساب AUC المرجع بعد
        r_auc = m_ref['auc'] if m_ref['auc'] > 0 else 1.0
        
        for name in list(mets.keys())[1:]:
            m_t = mets[name]
            ratio = (m_t['auc'] / r_auc) * 100
            st.write(f"**{name}**")
            color = "green" if 80 <= ratio <= 125 else "red"
            st.markdown(f"<span style='color:{color}; font-weight:bold;'>AUC Ratio: {ratio:.1f}%</span>", unsafe_allow_html=True)
            st.progress(min(ratio/150, 1.0))

    st.divider()
    st.subheader("📋 تقرير إحصائي مفصل")
    report_list = []
    for name, m in mets.items():
        report_list.append({
            "التركيبة": name,
            "Cmax (mg/L)": f"{m['cmax']:.2f}",
            "Tmax (h)": f"{m['tmax']:.2f}",
            "AUC (0-24)": f"{m['auc']:.2f}",
            "Bioequivalence": "✅ Pass" if name == "Reference (RLD)" or (80 <= (m['auc']/r_auc)*100 <= 125) else "❌ Fail"
        })
    st.table(pd.DataFrame(report_list))

else:
    st.info("الرجاء الضغط على زر 'تشغيل التحليل' لبدء المحاكاة واستخراج النتائج.")

st.caption("Sama Pharma Tech | R&D Excellence Hub v6.0 - 2026")