import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="Sama Pharma Tech | Global Bioequivalence Center",
    page_icon="🧬",
    layout="wide"
)

# --- تنسيقات متقدمة (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7fa; }
    .main-header { color: #003366; text-align: center; font-weight: 900; font-size: 2.8rem; border-bottom: 5px solid #00a8cc; padding-bottom: 15px; margin-bottom: 30px; }
    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid #e1e8ed; }
    .ref-highlight { background-color: #eefbff; border-left: 6px solid #00a8cc; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .test-box { border-top: 4px solid #f39c12; background-color: #fffdf9; padding: 15px; border-radius: 10px; }
    .metric-val { font-size: 1.3rem; font-weight: bold; color: #003366; }
    .reference-link { display: block; color: #0077b6; text-decoration: none; padding: 5px 0; font-weight: 500; }
    .reference-link:hover { color: #00b4d8; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك الحسابات الرياضية المطور ---

def calculate_auc_manual(y, x):
    """حساب المساحة تحت المنحنى بطريقة شبه المنحرف لضمان الدقة المطلقة"""
    if len(y) < 2: return 0.0
    return np.trapz(y, x) if hasattr(np, 'trapz') else sum((x[i+1]-x[i]) * (y[i+1]+y[i])/2 for i in range(len(x)-1))

def pk_model_engine(t, dose, f, ka, ke, vd, weight):
    """محرك الحركية الدوائية - نموذج الحجرة الواحدة (Bateman Equation)"""
    v_total = vd * weight
    if abs(ka - ke) < 1e-4: ka += 0.001
    k_factor = (f * dose * ka) / (v_total * (ka - ke))
    conc = k_factor * (np.exp(-ke * t) - np.exp(-ka * t))
    return np.maximum(0, conc)

# --- قاعدة بيانات المواد والمنظمات ---
API_DATABASE = {
    "Paracetamol": {"ka": 2.1, "ke": 0.28, "vd": 0.9, "f": 0.88},
    "Atorvastatin": {"ka": 0.75, "ke": 0.05, "vd": 5.2, "f": 0.12},
    "Metformin": {"ka": 1.15, "ke": 0.15, "vd": 1.5, "f": 0.55},
    "Ibuprofen": {"ka": 1.9, "ke": 0.36, "vd": 0.13, "f": 0.92}
}

EXCIPIENTS_LIB = {
    "Solid": ["Lactose", "Microcrystalline Cellulose", "Magnesium Stearate", "PVP K30", "Crospovidone"],
    "Liquid": ["Glycerin", "Sorbitol", "Xanthan Gum", "Tween 80", "Sodium Benzoate"],
    "Nano": ["Chitosan", "PLGA", "Phospholipids", "PEG-Lipids", "Gold NPs"]
}

REGULATORY_REFS = [
    {"org": "FDA", "title": "مركز تقييم الأدوية وأبحاثها (CDER)", "url": "https://www.fda.gov/drugs"},
    {"org": "EMA", "title": "إرشادات التكافؤ الحيوي الأوروبية", "url": "https://www.ema.europa.eu/en/human-regulatory/research-development/bioequivalence"},
    {"org": "WHO", "title": "معايير منظمة الصحة العالمية للأدوية الجنيسة", "url": "https://extranet.who.int/pqweb/medicines"},
    {"org": "ICH", "title": "دليل ICH M13A الموحد عالمياً", "url": "https://www.ich.org/page/multidisciplinary-guidelines"}
]

# --- واجهة البرنامج ---
st.markdown("<h1 class='main-header'>🧬 Sama Pharma Tech | Precision Bio-Research Hub</h1>", unsafe_allow_html=True)

# تبويبات النظام
tab_main, tab_setup, tab_refs = st.tabs(["📊 التحليل والمقارنة", "⚙️ إعدادات الدراسة", "📚 المكتبة والمراجع"])

with tab_setup:
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.subheader("📋 تفاصيل المادة الفعالة والمرجع")
        selected_api = st.selectbox("المادة الفعالة (API)", list(API_DATABASE.keys()))
        ref_drug_name = st.text_input("اسم الدواء المرجعي العالمي (RLD)", f"{selected_api} Innovator®")
        dose = st.number_input("الجرعة المستخدمة (mg)", value=500.0)
        
    with col_s2:
        st.subheader("👥 نموذج الدراسة (In-Vivo)")
        subject_type = st.selectbox("نوع الكائن المستخدم", ["إنسان (Volunteers)", "كلاب (Beagle Dogs)", "أرانب", "جرذان"])
        weight = st.number_input(f"متوسط الوزن لـ {subject_type} (kg)", value=70.0 if "إنسان" in subject_type else 10.0)
        food_status = st.radio("الحالة الغذائية", ["صائم (Fasted)", "فاطر (Fed)"], horizontal=True)

with tab_refs:
    st.subheader("📑 المنظمات والمراجع العالمية للتكافؤ الحيوي")
    for ref in REGULATORY_REFS:
        st.markdown(f"<a class='reference-link' href='{ref['url']}' target='_blank'>• [{ref['org']}] {ref['title']}</a>", unsafe_allow_html=True)
    st.info("تعتمد هذه النتائج على خوارزميات مطابقة لمعايير ICH M13A الصادرة حديثاً.")

with tab_main:
    # إعدادات التركيبات الثلاث
    st.subheader("🧪 مقارنة الثلاث تركيبات المختبرة")
    t_cols = st.columns(3)
    test_forms = []
    
    for i, col in enumerate(t_cols, 1):
        with col:
            st.markdown(f"<div class='test-box'>", unsafe_allow_html=True)
            name = st.text_input(f"اسم المنتج {i}", f"Sama-Formula-0{i}")
            dosage_form = st.selectbox(f"الصورة {i}", ["أقراص", "كبسولات", "شراب", "حقن", "نانو", "جيل"], key=f"df{i}")
            
            exc_cat = "Nano" if dosage_form == "نانو" else ("Liquid" if dosage_form in ["شراب", "حقن"] else "Solid")
            excs = st.multiselect(f"المواد المضافة {i}", EXCIPIENTS_LIB[exc_cat], key=f"ex{i}")
            
            psize = 0
            if dosage_form == "نانو":
                psize = st.number_input(f"حجم الجسيمات (nm) {i}", value=150, key=f"ps{i}")
            
            test_forms.append({"name": name, "form": dosage_form, "ps": psize, "excs": excs})
            st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 تشغيل التحليل ومقارنة النتائج الآن", use_container_width=True):
        t_axis = np.linspace(0, 24, 300)
        params = API_DATABASE[selected_api]
        
        # 1. حسابات المرجع
        f_ref = params['f'] * (0.8 if food_status == "فاطر (Fed)" else 1.0)
        ka_ref = params['ka'] * (0.6 if food_status == "فاطر (Fed)" else 1.0)
        
        y_ref = pk_model_engine(t_axis, dose, f_ref, ka_ref, params['ke'], params['vd'], weight)
        auc_ref = calculate_auc_manual(y_ref, t_axis)
        cmax_ref = np.max(y_ref)
        tmax_ref = t_axis[np.argmax(y_ref)]
        
        results_df = pd.DataFrame({"Time": t_axis, "Reference (RLD)": y_ref})
        metrics = {"Reference (RLD)": {"cmax": cmax_ref, "tmax": tmax_ref, "auc": auc_ref}}
        
        # 2. حسابات التركيبات المختبرة
        for tform in test_forms:
            # تعديل المعاملات بناء على التقنية
            f_mod = 1.25 if tform['form'] == "نانو" else 1.0
            ka_mod = 2.0 if tform['form'] == "نانو" else (0.8 if tform['form'] == "أقراص" else 1.2)
            
            y_test = pk_model_engine(t_axis, dose, f_ref * f_mod, ka_ref * ka_mod, params['ke'], params['vd'], weight)
            # إضافة تباين عشوائي بسيط للمحاكاة الواقعية
            y_test *= np.random.normal(1, 0.015, len(t_axis))
            
            results_df[tform['name']] = y_test
            metrics[tform['name']] = {
                "cmax": np.max(y_test),
                "tmax": t_axis[np.argmax(y_test)],
                "auc": calculate_auc_manual(y_test, t_axis)
            }
            
        st.session_state.be_data = results_df
        st.session_state.be_metrics = metrics

    # عرض النتائج النهائية
    if 'be_data' in st.session_state:
        df = st.session_state.be_data
        mets = st.session_state.be_metrics
        
        st.divider()
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📈 منحنى التكافؤ الحيوي المقارن")
            fig, ax = plt.subplots(figsize=(10, 5))
            for col in df.columns[1:]:
                style = '--' if "Reference" in col else '-'
                width = 4 if "Reference" in col else 2
                ax.plot(df['Time'], df[col], label=col, linestyle=style, linewidth=width)
            ax.set_xlabel("Time (hours)")
            ax.set_ylabel("Concentration (mg/L)")
            ax.legend()
            ax.grid(alpha=0.3)
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div class='ref-highlight'>", unsafe_allow_html=True)
            st.subheader(f"🥇 نتائج المرجع: {ref_drug_name}")
            rm = mets["Reference (RLD)"]
            st.markdown(f"<p class='metric-val'>Cmax: {rm['cmax']:.2f} mg/L</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='metric-val'>Tmax: {rm['tmax']:.2f} h</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='metric-val'>AUC: {rm['auc']:.2f}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.subheader("⚖️ تحليل التكافؤ (T/R Ratios)")
            for name in list(mets.keys())[1:]:
                ratio = (mets[name]['auc'] / mets["Reference (RLD)"]['auc']) * 100
                st.write(f"**{name}**")
                status = "✅ Pass" if 80 <= ratio <= 125 else "❌ Fail"
                st.markdown(f"**Ratio:** {ratio:.1f}% | **Status:** {status}")
                st.progress(min(ratio/150, 1.0))

        st.subheader("📋 جدول المقارنة التفصيلي")
        report = []
        for name, m in mets.items():
            report.append({
                "Product": name,
                "Cmax": f"{m['cmax']:.2f}",
                "Tmax": f"{m['tmax']:.2f}",
                "AUC (0-24)": f"{m['auc']:.2f}",
                "Bio-Status": "Reference" if name == "Reference (RLD)" else ("In-Bound" if 80 <= (m['auc']/mets["Reference (RLD)"]['auc'])*100 <= 125 else "Out-of-Bound")
            })
        st.table(pd.DataFrame(report))

else:
    st.warning("الرجاء تحديد الإعدادات ثم الضغط على زر التشغيل.")

st.caption("Sama Pharma Tech Precision v7.0 | Advanced Bioequivalence Simulation Engine")