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

# --- قاعدة بيانات المواد والمنظمات والمراجع ---
API_DATA = {
    "Paracetamol": {"ka": 2.1, "ke": 0.28, "vd": 0.9, "f": 0.88},
    "Atorvastatin": {"ka": 0.8, "ke": 0.05, "vd": 5.2, "f": 0.12},
    "Metformin": {"ka": 1.1, "ke": 0.15, "vd": 1.5, "f": 0.55},
    "Custom": {"ka": 1.0, "ke": 0.1, "vd": 1.0, "f": 0.7}
}

EXCIPIENTS = {
    "Tablets/Capsules": ["Lactose", "Starch", "Mg Stearate", "Talc", "MCC", "PVP", "Crospovidone"],
    "Gelatin Capsules": ["Gelatin", "Glycerin", "Sorbitol", "Titanium Dioxide", "Water"],
    "Syrup/Liquids": ["Sucrose", "Glycerin", "Propylene Glycol", "Xanthan Gum", "Sodium Benzoate"],
    "Ampoules/Vials": ["WFI", "Sodium Chloride", "Benzyl Alcohol", "Phosphate Buffer"],
    "Nano/Advanced": ["Chitosan", "PLGA", "Phospholipids", "PEG", "Gold NPs", "Silica"]
}

REGULATORY_REFS = {
    "FDA - CDER": "https://www.fda.gov/drugs/guidances-drugs/bioequivalence-recommendations-specific-products",
    "EMA - Guidelines": "https://www.ema.europa.eu/en/human-regulatory/research-development/bioequivalence",
    "WHO - Standards": "https://extranet.who.int/pqweb/medicines",
    "ICH - M13A": "https://www.ich.org/page/multidisciplinary-guidelines"
}

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022243.png", width=80)
    st.header("⚙️ إعدادات الدراسة In-Vivo")
    
    api_choice = st.selectbox("المادة الفعالة (API)", list(API_DATA.keys()))
    user_dose = st.number_input("الجرعة المستخدمة (mg)", value=500.0)
    
    st.divider()
    st.subheader("👥 بيانات الكائن المستخدم")
    subject = st.selectbox("نوع الكائن", ["Human (إنسان)", "Animal (Beagle Dog)", "Animal (Rat)", "Animal (Rabbit)"])
    weight = st.number_input("وزن الكائن (kg)", value=70.0 if "Human" in subject else 10.0)
    food_status = st.radio("الحالة الغذائية", ["صائم (Fasted)", "فاطر (Fed)"], horizontal=True)

# --- الواجهة الرئيسية ---
st.markdown("<div class='main-header'>Sama Pharma Tech | Precision Bioequivalence Hub v8.0</div>", unsafe_allow_html=True)

tab_calc, tab_refs = st.tabs(["📊 التحليل والمقارنة الثلاثية", "📚 المراجع والمكتبة"])

with tab_refs:
    st.subheader("📚 المنظمات والمراجع العالمية المعتمدة")
    for name, url in REGULATORY_REFS.items():
        st.markdown(f"🔗 [{name}]({url}) - دليل إرشادات التكافؤ الحيوي والدراسات السريرية.")
    st.info("تم تحديث المكتبة لتشمل معايير ICH M13A لضمان قبول النتائج دولياً.")

with tab_calc:
    col_ref, col_space = st.columns([1, 0.05]) # مسافة بسيطة بين المرجع والاختبار
    
    with col_ref:
        st.markdown("<div class='reference-section'>", unsafe_allow_html=True)
        st.subheader("🚩 الدواء المرجعي العالمي (RLD)")
        ref_name = st.text_input("اسم الدواء المرجعي", "Innovator Standard")
        r_cmax = st.number_input("Cmax المرجع (Target)", value=12.5)
        r_tmax = st.number_input("Tmax المرجع (Target)", value=1.5)
        r_auc = st.number_input("AUC المرجع (Target)", value=85.0)
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("🧪 تركيبات الاختبار المختبرة (3 Formulations)")
    t_cols = st.columns(3)
    formulations = []

    for i in range(3):
        with t_cols[i]:
            st.markdown(f"<div class='test-box'>", unsafe_allow_html=True)
            st.markdown(f"**التركيبة {i+1}**")
            f_name = st.text_input(f"الاسم", f"Sama-Formula-{i+1}", key=f"n{i}")
            f_type = st.selectbox(f"الصورة الصيدلانية", ["Tablets", "Capsules", "Gelatin Cap", "Syrup", "Ampoule", "Nano"], key=f"t{i}")
            
            # تحديد قائمة الإضافات بناء على الصورة الصيدلانية
            if f_type == "Nano": exc_cat = "Nano/Advanced"
            elif f_type in ["Syrup"]: exc_cat = "Syrup/Liquids"
            elif f_type == "Ampoule": exc_cat = "Ampoules/Vials"
            elif f_type == "Gelatin Cap": exc_cat = "Gelatin Capsules"
            else: exc_cat = "Tablets/Capsules"
            
            selected_excs = st.multiselect("المواد المضافة", EXCIPIENTS[exc_cat], key=f"e{i}")
            
            p_size = 0
            if f_type == "Nano":
                p_size = st.number_input("حجم الجسيمات (nm)", value=150, key=f"p{i}")
            
            formulations.append({"name": f_name, "type": f_type, "excs": selected_excs, "psize": p_size})
            st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 تشغيل تحليل التكافؤ الحيوي والمقارنة الشاملة", use_container_width=True):
        t_points = np.linspace(0, 24, 300)
        base_p = API_DATA[api_choice]
        
        # 1. محاكاة المرجع (RLD)
        # تعديل العوامل بناء على الحالة الغذائية
        f_status = 0.85 if food_status == "فاطر (Fed)" else 1.0
        y_ref = pk_model(t_points, user_dose, base_p['f'] * f_status, base_p['ka'], base_p['ke'], base_p['vd'], weight)
        # تطبيع المنحنى ليناسب مدخلات المستخدم للمرجع
        if np.max(y_ref) > 0: y_ref = y_ref * (r_cmax / np.max(y_ref))
        
        sim_results = {"Time": t_points, "Reference": y_ref}
        metrics = {"Reference": {"cmax": np.max(y_ref), "tmax": t_points[np.argmax(y_ref)], "auc": safe_auc(y_ref, t_points)}}
        
        # 2. محاكاة التركيبات الثلاث
        for f in formulations:
            # تأثير الصورة الصيدلانية والنانو على الامتصاص
            ka_mod = 2.8 if f['type'] == "Nano" else (1.6 if f['type'] in ["Syrup", "Ampoule"] else 1.0)
            f_mod = 1.3 if f['type'] == "Nano" else 1.0
            
            # تأثير حجم الجسيمات في حالة النانو
            if f['type'] == "Nano" and f['psize'] < 100:
                ka_mod *= 1.2
                f_mod *= 1.1
                
            y_test = pk_model(t_points, user_dose, base_p['f'] * f_mod * f_status, base_p['ka'] * ka_mod, base_p['ke'], base_p['vd'], weight)
            # إضافة تباين عشوائي بسيط للمحاكاة (In-Vivo Variation)
            y_test *= np.random.normal(1.0, 0.02, len(t_points))
            
            sim_results[f['name']] = y_test
            metrics[f['name']] = {
                "cmax": np.max(y_test),
                "tmax": t_points[np.argmax(y_test)],
                "auc": safe_auc(y_test, t_points)
            }

        # --- عرض النتائج ---
        st.divider()
        res_col1, res_col2 = st.columns([2, 1])
        
        with res_col1:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(t_points, y_ref, label=f"المرجع: {ref_name}", linewidth=4, color='black', linestyle='--')
            for f in formulations:
                ax.plot(t_points, sim_results[f['name']], label=f"اختبار: {f['name']}", linewidth=2.5)
            
            ax.set_title("In-Vivo Comparative Bioavailability Profile")
            ax.set_xlabel("Time (hours)")
            ax.set_ylabel("Plasma Conc (µg/mL)")
            ax.legend()
            ax.grid(True, alpha=0.2)
            st.pyplot(fig)
            
        with res_col2:
            st.subheader("📏 المقاييس الحيوية (In-Vivo Results)")
            for name, m in metrics.items():
                with st.expander(f"بيانات {name}", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Cmax", f"{m['cmax']:.2f}")
                    c2.metric("Tmax", f"{m['tmax']:.2f}")
                    c3.metric("AUC", f"{m['auc']:.1f}")
                    
                    if name != "Reference":
                        ratio = (m['auc'] / metrics["Reference"]['auc']) * 100 if metrics["Reference"]['auc'] > 0 else 0
                        status = "✅ Pass" if 80 <= ratio <= 125 else "❌ Fail"
                        st.write(f"**نسبة التكافؤ:** {ratio:.1f}% | **النتيجة:** {status}")

        st.subheader("📝 تقرير التركيبات والمواد المضافة")
        report_data = []
        for f in formulations:
            m = metrics[f['name']]
            report_data.append({
                "اسم التركيبة": f['name'],
                "الصورة الصيدلانية": f['type'],
                "المواد المضافة": ", ".join(f['excs']),
                "حجم الجسيمات (نانو)": f"{f['psize']} nm" if f['psize'] > 0 else "N/A",
                "Cmax/Ref %": f"{(m['cmax']/metrics['Reference']['cmax'])*100:.1f}%"
            })
        st.table(pd.DataFrame(report_data))
        
        # تحميل البيانات
        csv = pd.DataFrame(sim_results).to_csv(index=False)
        st.download_button("📂 تحميل التقرير الكامل (CSV)", csv, "bioequivalence_full_report.csv", "text/csv")

st.markdown("<br><hr><center>Sama Pharma Tech | وحدة أبحاث التكافؤ الحيوي المتطورة</center>", unsafe_allow_html=True)