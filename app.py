import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- الإعدادات الأساسية ---
st.set_page_config(
    page_title="Sama Pharma Tech | Precision v8.0",
    page_icon="🧬",
    layout="wide"
)

# --- تنسيقات الواجهة (CSS) ---
st.markdown("""
    <style>
    .main-header { color: #003366; text-align: center; font-weight: 900; font-size: 2.5rem; padding: 20px; background: #eefbff; border-radius: 15px; margin-bottom: 25px; border: 2px solid #00a8cc; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; border-right: 5px solid #00a8cc; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .reference-section { background: #f0f4f8; padding: 20px; border-radius: 15px; border: 1px solid #d1d9e6; }
    .test-box { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e1e8ed; margin-bottom: 10px; }
    .sidebar-header { font-size: 1.2rem; font-weight: bold; color: #003366; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك الحسابات الرياضية المطور ---
def safe_auc(y, x):
    """حساب المساحة تحت المنحنى بطريقة شبه المنحرف لضمان الاستقرار"""
    try:
        y = np.array(y)
        x = np.array(x)
        return np.sum((x[1:] - x[:-1]) * (y[1:] + y[:-1]) / 2.0)
    except:
        return 0.0

def pk_model(t, dose, f, ka, ke, vd, weight):
    """نموذج الحركية الدوائية لمحاكاة نتائج In-Vivo"""
    try:
        v_total = vd * weight
        if abs(ka - ke) < 1e-5: ka += 0.01
        # معادلة بيتمان (Bateman Equation)
        conc = (f * dose * ka) / (v_total * (ka - ke)) * (np.exp(-ke * t) - np.exp(-ka * t))
        return np.maximum(0, conc)
    except:
        return np.zeros_like(t)

# --- قاعدة بيانات الأدوية الموسعة ---
API_DATA = {
    "Paracetamol": {"ka": 2.1, "ke": 0.28, "vd": 0.9, "f": 0.88},
    "Atorvastatin": {"ka": 0.8, "ke": 0.05, "vd": 5.2, "f": 0.12},
    "Metformin": {"ka": 1.1, "ke": 0.15, "vd": 1.5, "f": 0.55},
    "Amoxicillin": {"ka": 1.5, "ke": 0.45, "vd": 0.3, "f": 0.90},
    "Ibuprofen": {"ka": 2.5, "ke": 0.35, "vd": 0.1, "f": 0.95},
    "Ciprofloxacin": {"ka": 1.2, "ke": 0.2, "vd": 2.5, "f": 0.70},
    "Gliclazide": {"ka": 0.5, "ke": 0.08, "vd": 0.2, "f": 0.85},
    "Omeprazole": {"ka": 1.8, "ke": 0.6, "vd": 0.3, "f": 0.40},
    "Custom": {"ka": 1.0, "ke": 0.1, "vd": 1.0, "f": 0.7}
}

# --- قاعدة بيانات المواد المضافة لكل صورة صيدلانية ---
EXCIPIENTS = {
    "Tablets (أقراص)": ["Lactose", "Starch", "Mg Stearate", "Talc", "MCC", "PVP", "Crospovidone", "HPMC"],
    "Capsules (كبسولات)": ["Lactose", "Starch", "Mg Stearate", "Sodium Lauryl Sulfate", "Silica"],
    "Gelatin Cap (جيلاتين)": ["Gelatin", "Glycerin", "Sorbitol", "Titanium Dioxide", "Water", "Methylparaben"],
    "Syrup (شراب)": ["Sucrose", "Glycerin", "Propylene Glycol", "Xanthan Gum", "Sodium Benzoate", "Flavoring"],
    "Ampoule (أمبول)": ["WFI", "Sodium Chloride", "Benzyl Alcohol", "Phosphate Buffer", "Hydrochloric Acid"],
    "Nano (نانو)": ["Chitosan", "PLGA", "Phospholipids", "PEG", "Gold NPs", "Silica", "Poloxamer"],
    "Suspension (معلق)": ["CMC", "Avicel", "Simethicone", "Saccharin Sodium", "Polysorbate 80"]
}

# --- المكتبة والمنظمات ---
REGULATORY_REFS = {
    "FDA - CDER": "https://www.fda.gov/drugs/guidances-drugs/bioequivalence-recommendations-specific-products",
    "EMA - Guidelines": "https://www.ema.europa.eu/en/human-regulatory/research-development/bioequivalence",
    "WHO - Standards": "https://extranet.who.int/pqweb/medicines",
    "ICH - M13A": "https://www.ich.org/page/multidisciplinary-guidelines",
    "SFDA - Saudi Food & Drug": "https://www.sfda.gov.sa/en/drugs-guidelines",
    "USP-NF Database": "https://www.usp.org/usp-nf"
}

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022243.png", width=80)
    st.markdown("<div class='sidebar-header'>⚙️ إعدادات الدراسة In-Vivo</div>", unsafe_allow_html=True)
    
    api_choice = st.selectbox("اختر المادة الفعالة (API)", list(API_DATA.keys()))
    user_dose = st.number_input("الجرعة الكلية (mg)", value=500.0)
    
    st.divider()
    st.markdown("<div class='sidebar-header'>👥 بيانات الكائن المستخدم</div>", unsafe_allow_html=True)
    subject = st.selectbox("نوع الكائن", ["Human (إنسان)", "Animal (Beagle Dog)", "Animal (Rat)", "Animal (Rabbit)"])
    weight = st.number_input("وزن الكائن (kg)", value=70.0 if "Human" in subject else 10.0)
    food_status = st.radio("الحالة الغذائية", ["صائم (Fasted)", "فاطر (Fed)"], horizontal=True)

# --- الواجهة الرئيسية ---
st.markdown("<div class='main-header'>Sama Pharma Tech | Precision Bioequivalence Hub v8.0</div>", unsafe_allow_html=True)

tab_calc, tab_refs = st.tabs(["📊 التحليل والمقارنة الثلاثية", "📚 المراجع والمكتبة"])

with tab_refs:
    st.subheader("📚 المنظمات والمراجع العالمية المعتمدة")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        for name, url in list(REGULATORY_REFS.items())[:3]:
            st.markdown(f"🔗 [{name}]({url})")
    with col_r2:
        for name, url in list(REGULATORY_REFS.items())[3:]:
            st.markdown(f"🔗 [{name}]({url})")
    st.info("تم تحديث المكتبة لتشمل معايير ICH M13A و SFDA لضمان قبول النتائج محلياً ودولياً.")

with tab_calc:
    # إعدادات الدواء المرجعي
    st.markdown("<div class='reference-section'>", unsafe_allow_html=True)
    st.subheader("🚩 الدواء المرجعي العالمي (RLD)")
    c_r1, c_r2, c_r3, c_r4 = st.columns(4)
    ref_name = c_r1.text_input("اسم الدواء المرجعي", "Reference Product")
    r_cmax = c_r2.number_input("Cmax المرجع", value=12.5)
    r_tmax = c_r3.number_input("Tmax المرجع", value=1.5)
    r_auc = c_r4.number_input("AUC المرجع", value=85.0)
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("🧪 تركيبات الاختبار الثلاثة (Test Formulations)")
    t_cols = st.columns(3)
    formulations = []

    for i in range(3):
        with t_cols[i]:
            st.markdown(f"<div class='test-box'>", unsafe_allow_html=True)
            st.markdown(f"**التركيبة المختبرة {i+1}**")
            f_name = st.text_input(f"اسم التركيبة", f"Formulation-{i+1}", key=f"n{i}")
            f_type = st.selectbox(f"الصورة الصيدلانية", list(EXCIPIENTS.keys()), key=f"t{i}")
            
            selected_excs = st.multiselect("المواد المضافة", EXCIPIENTS[f_type], key=f"e{i}")
            
            p_size = 0
            if "Nano" in f_type:
                p_size = st.number_input("حجم الجسيمات (nm)", value=150, key=f"p{i}")
            
            formulations.append({"name": f_name, "type": f_type, "excs": selected_excs, "psize": p_size})
            st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 تشغيل تحليل التكافؤ الحيوي والمقارنة الشاملة", use_container_width=True):
        t_points = np.linspace(0, 24, 300)
        base_p = API_DATA[api_choice]
        
        # تأثير الحالة الغذائية
        f_status = 0.80 if food_status == "فاطر (Fed)" else 1.0
        
        # 1. محاكاة المرجع (RLD)
        y_ref = pk_model(t_points, user_dose, base_p['f'] * f_status, base_p['ka'], base_p['ke'], base_p['vd'], weight)
        if np.max(y_ref) > 0: y_ref = y_ref * (r_cmax / np.max(y_ref))
        
        sim_results = {"Time": t_points, "Reference": y_ref}
        metrics = {"Reference": {"cmax": np.max(y_ref), "tmax": t_points[np.argmax(y_ref)], "auc": safe_auc(y_ref, t_points)}}
        
        # 2. محاكاة تركيبات الاختبار
        for f in formulations:
            # تعديل العوامل بناء على الصورة الصيدلانية
            ka_mod = 1.0
            f_mod = 1.0
            
            if "Nano" in f['type']:
                ka_mod = 3.0
                f_mod = 1.4
                if f['psize'] < 100: ka_mod *= 1.3 # جزيئات أصغر = امتصاص أسرع
            elif "Syrup" in f['type'] or "Ampoule" in f['type']:
                ka_mod = 1.8
                f_mod = 1.1
            elif "Gelatin" in f['type']:
                ka_mod = 1.2
            
            y_test = pk_model(t_points, user_dose, base_p['f'] * f_mod * f_status, base_p['ka'] * ka_mod, base_p['ke'], base_p['vd'], weight)
            # تباين In-Vivo
            y_test *= np.random.normal(1.0, 0.03, len(t_points))
            
            sim_results[f['name']] = y_test
            metrics[f['name']] = {
                "cmax": np.max(y_test),
                "tmax": t_points[np.argmax(y_test)],
                "auc": safe_auc(y_test, t_points)
            }

        # --- عرض النتائج المتقدمة ---
        st.divider()
        res_col1, res_col2 = st.columns([2, 1])
        
        with res_col1:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(t_points, y_ref, label=f"المرجع: {ref_name}", linewidth=4, color='#1e293b', linestyle='--')
            colors = ['#00a8cc', '#ff6b6b', '#51cf66']
            for idx, f in enumerate(formulations):
                ax.plot(t_points, sim_results[f['name']], label=f"اختبار: {f['name']}", linewidth=2.5, color=colors[idx])
            
            ax.set_title(f"In-Vivo PK Profile: {subject} ({food_status})")
            ax.set_xlabel("Time (hours)")
            ax.set_ylabel("Concentration (µg/mL)")
            ax.legend()
            ax.grid(True, alpha=0.15)
            st.pyplot(fig)
            
        with res_col2:
            st.subheader("📏 المقاييس الحيوية (PK Results)")
            for name, m in metrics.items():
                with st.expander(f"بيانات {name}", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Cmax", f"{m['cmax']:.2f}")
                    c2.metric("Tmax", f"{m['tmax']:.2f}")
                    c3.metric("AUC", f"{m['auc']:.1f}")
                    
                    if name != "Reference":
                        ratio = (m['auc'] / metrics["Reference"]['auc']) * 100 if metrics["Reference"]['auc'] > 0 else 0
                        status = "✅ Pass" if 80 <= ratio <= 125 else "❌ Fail"
                        st.write(f"**Bioequivalence Ratio:** {ratio:.1f}% | {status}")

        st.subheader("📝 التقرير الفني للتركيبات")
        report_data = []
        for f in formulations:
            m = metrics[f['name']]
            report_data.append({
                "اسم التركيبة": f['name'],
                "الصورة الصيدلانية": f['type'],
                "المواد المضافة": ", ".join(f['excs']),
                "حجم الجسيمات": f"{f['psize']} nm" if f['psize'] > 0 else "N/A",
                "Cmax Relative": f"{(m['cmax']/metrics['Reference']['cmax'])*100:.1f}%",
                "AUC Relative": f"{(m['auc']/metrics['Reference']['auc'])*100:.1f}%"
            })
        st.table(pd.DataFrame(report_data))
        
        csv = pd.DataFrame(sim_results).to_csv(index=False)
        st.download_button("📂 تحميل التقرير التفصيلي (CSV)", csv, "precision_be_study.csv", "text/csv")

st.markdown("<br><hr><center>Sama Pharma Tech | وحدة أبحاث التكافؤ الحيوي المتطورة</center>", unsafe_allow_html=True)