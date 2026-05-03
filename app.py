import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- إعدادات الصفحة الرسمية ---
st.set_page_config(
    page_title="Sama Pharma Tech | Bio-Analyzer",
    page_icon="💊",
    layout="wide"
)

# --- تحسين المظهر باستخدام CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-header { color: #1A237E; font-weight: bold; text-align: center; font-size: 2.2rem; }
    .sidebar .sidebar-content { background-color: #ffffff; }
    .stButton>button { background-color: #1A237E; color: white; border-radius: 8px; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #0D47A1; border-color: #0D47A1; }
    .info-card { padding: 15px; border-radius: 10px; background-color: #e3f2fd; border-left: 5px solid #1A237E; margin-bottom: 20px; }
    .metric-container { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🔬 Sama Pharma Tech | Bio-Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>نظام تحليل التكافؤ الحيوي المتقدم للصناعات الدوائية والنانوية</p>", unsafe_allow_html=True)

st.divider()

# إدارة حالة البيانات باستخدام Session State لضمان التحديث المستمر
if 'df_data' not in st.session_state:
    st.session_state.df_data = None

# --- القائمة الجانبية: إدخال البيانات ---
with st.sidebar:
    st.header("📂 معلومات الدراسة")
    study_id = st.text_input("رقم البروتوكول (Study ID)", "SPT-BIO-2024-001")
    drug_api = st.text_input("المادة الفعالة (API)", "Paracetamol")
    
    st.divider()
    
    st.header("🧪 تفاصيل التركيبة (Formulation)")
    dosage_form = st.selectbox("الشكل الصيدلاني", ["الأنظمة النانوية (Nano)", "الأشكال الصلبة (Solid)", "الأشكال السائلة (Liquid)"])
    
    if "Nano" in dosage_form:
        carrier = st.selectbox("مادة التحميل النانوية", [
            "الجسيمات الشحمية (Liposomes)", 
            "الجسيمات النانوية البوليمرية (Polymeric NPs)", 
            "النانو سليلوز (Nano-Cellulose)",
            "الجسيمات النانوية المعدنية (Gold/Silver NPs)"
        ])
    elif "Solid" in dosage_form:
        carrier = st.selectbox("مادة التحميل الصلبة", [
            "اللاكتوز (Lactose)", 
            "الميكروكريستالين سليلوز (MCC)", 
            "النشا (Starch)", 
            "البوفيدون (PVP)"
        ])
    else:
        carrier = st.selectbox("مادة التحميل السائلة", [
            "الجلسرين (Glycerin)", 
            "البروبيلين جليكول (Propylene Glycol)", 
            "التوين (Tween 80)",
            "الماء المقطر (Distilled Water)"
        ])

    test_brand = st.text_input("اسم المنتج التجريبي (Test)", "Sama-Test")
    ref_brand = st.text_input("اسم المنتج المرجعي (Ref)", "Reference-Market")
    
    st.divider()
    
    st.header("📊 إدارة البيانات")
    file_upload = st.file_uploader("رفع ملف (CSV/Excel)", type=["csv", "xlsx"])
    
    if file_upload is not None:
        if file_upload.name.endswith('.csv'):
            st.session_state.df_data = pd.read_csv(file_upload)
        else:
            st.session_state.df_data = pd.read_excel(file_upload)
    
    st.write("أو اختبر ببيانات جاهزة:")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 قياسي"):
            sample = {
                'Time': [0, 0.5, 1, 2, 4, 8, 12, 24],
                'Reference': [0, 15.2, 28.4, 30.1, 18.5, 8.2, 3.1, 0.5],
                'Test': [0, 14.8, 27.9, 29.5, 19.1, 9.0, 3.8, 0.6]
            }
            st.session_state.df_data = pd.DataFrame(sample)
    with c2:
        if st.button("🧪 نانو"):
            nano_sample = {
                'Time': [0, 0.25, 0.5, 1, 2, 4, 8, 12, 24],
                'Reference': [0, 8.5, 15.2, 28.4, 29.5, 18.2, 8.4, 3.1, 0.5],
                'Test': [0, 22.1, 38.4, 45.2, 32.5, 15.2, 6.1, 2.2, 0.3]
            }
            st.session_state.df_data = pd.DataFrame(nano_sample)

# --- الدوال الرياضية لحساب البارامترات ---
def calc_auc(time, conc):
    return np.trapz(conc, time)

def calc_thalf(time, conc):
    try:
        valid_idx = conc > 0
        if np.sum(valid_idx) < 3: return 0
        log_c = np.log(conc[valid_idx][-3:]) 
        t_subset = time[valid_idx][-3:]
        slope, _ = np.polyfit(t_subset, log_c, 1)
        ke = -slope
        return 0.693 / ke if ke > 0 else 0
    except:
        return 0

# --- عرض النتائج والتحليل ---
if st.session_state.df_data is not None:
    df = st.session_state.df_data
    
    st.success(f"✅ تم تفعيل تحليل البروتوكول: {study_id} للمادة: {drug_api}")

    # ملخص الدراسة يتحدث تلقائياً مع تغيير المدخلات
    st.markdown(f"""
    <div class='info-card'>
        <strong>ملخص المكونات الرقابي (تم التحديث):</strong><br>
        المادة الفعالة: {drug_api} | نظام التحميل: {carrier} ({dosage_form})<br>
        المقارنة بين: {test_brand} (تجريبي) و {ref_brand} (مرجعي)
    </div>
    """, unsafe_allow_html=True)

    col_graph, col_stats = st.columns([2, 1])

    with col_graph:
        st.subheader(f"📊 ملف الحركية الدوائية لـ {drug_api}")
        fig, ax = plt.subplots(figsize=(10, 6))
        for col in df.columns[1:]:
            label = test_brand if "Test" in col else ref_brand
            color = "#1A237E" if "Test" in col else "#D32F2F"
            ax.plot(df['Time'], df[col], 'o-', label=label, linewidth=3, color=color)
            ax.fill_between(df['Time'], df[col], alpha=0.1, color=color)
            
        ax.set_xlabel("Time (h)", fontsize=12)
        ax.set_ylabel("Concentration (μg/mL)", fontsize=12)
        ax.set_title(f"Bioequivalence Study: {drug_api} ({study_id})", fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3, linestyle='--')
        st.pyplot(fig)

    with col_stats:
        st.subheader("📋 البارامترات الحركية")
        res_list = []
        for col in df.columns[1:]:
            cmax = df[col].max()
            tmax = df.loc[df[col] == cmax, 'Time'].values[0]
            auc = calc_auc(df['Time'], df[col])
            thalf = calc_thalf(df['Time'].values, df[col].values)
            
            brand = test_brand if "Test" in col else ref_brand
            res_list.append({'API': drug_api, 'Brand': brand, 'Cmax': cmax, 'Tmax': tmax, 'AUC': auc, 't½': thalf})
            
            with st.expander(f"نتائج {brand}", expanded=True):
                st.write(f"**Cmax:** {cmax:.2f} μg/mL")
                st.write(f"**Tmax:** {tmax:.2f} h")
                st.write(f"**AUC₀₋₂₄:** {auc:.2f} μg.h/mL")
                st.write(f"**t½:** {thalf:.2f} h")

        # تقرير التكافؤ الحيوي
        if len(res_list) >= 2:
            st.divider()
            st.subheader("⚖️ نتيجة التكافؤ الحيوي")
            auc_ratio = (res_list[1]['AUC'] / res_list[0]['AUC']) * 100
            cmax_ratio = (res_list[1]['Cmax'] / res_list[0]['Cmax']) * 100
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(f"نسبة AUC ({drug_api})", f"{auc_ratio:.2f}%")
            with c2:
                st.metric("نسبة Cmax", f"{cmax_ratio:.2f}%")
            
            if 80 <= auc_ratio <= 125 and 80 <= cmax_ratio <= 125:
                st.success(f"✅ التركيبة متكافئة لـ {drug_api}")
            else:
                st.error(f"❌ التركيبة غير متكافئة لـ {drug_api}")

    # تصدير التقرير متضمناً اسم الدواء والبروتوكول
    report_df = pd.DataFrame(res_list)
    csv_data = report_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(f"📥 تحميل تقرير {drug_api} (CSV)", csv_data, f"Regulatory_Report_{drug_api}_{study_id}.csv", "text/csv")

else:
    st.info("👋 مرحباً بك في منصة Sama Pharma Tech. يرجى إدخال اسم الدواء ثم الضغط على 'بيانات نانو' أو رفع ملفك.")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Pharmacokinetics_curve.svg/640px-Pharmacokinetics_curve.svg.png", caption="التمثيل البياني القياسي للحركية الدوائية")

st.divider()
st.caption(f"Sama Pharma Tech | نظام التحليل الرقمي الإصدار 2.1 | API Current: {drug_api if drug_api else 'غير محدد'}")