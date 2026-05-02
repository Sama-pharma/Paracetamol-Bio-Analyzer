import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. إعدادات الصفحة البرمجية
st.set_page_config(
    page_title="Bio-AI Paracetamol Analyzer",
    page_icon="💊",
    layout="wide"
)

# 2. تصميم الواجهة (العنوان والمقدمة)
st.title("🔬 منصة تحليل التكافؤ الحيوي: باراسيتامول")
st.markdown("""
هذه المنصة مخصصة لشركات الأدوية ومراكز الأبحاث (R&D) للمقارنة بين 
**الباراسيتامول التقليدي** و **التركيبات المطورة (Nano/Enhanced)**.
""")

st.divider()

# 3. القائمة الجانبية (Sidebar) لمدخلات المستخدم
with st.sidebar:
    st.header("⚙️ إعدادات التجربة")
    drug_name = "Paracetamol"
    dose = st.selectbox("الجرعة (mg)", [500, 1000], index=0)
    st.info("الباراسيتامول (Acetaminophen) هو النموذج المثالي لاختبار سرعة الامتصاص.")
    st.write("---")
    st.caption("تطوير: Bio-AI Analyzer Team")

# 4. محرك البيانات (بيانات افتراضية دقيقة للمعاينة)
# الوقت بالساعات
time = np.array([0, 0.25, 0.5, 0.75, 1, 1.5, 2, 4, 6, 8])

# تركيز الباراسيتامول التقليدي (Reference) μg/mL
conc_ref = [0, 5.2, 12.5, 18.2, 20.5, 15.1, 10.2, 4.5, 1.8, 0.5]

# تركيز الباراسيتامول المطور (Test - Nano/Enhanced) μg/mL
# نلاحظ هنا امتصاص أسرع وقمة أعلى
conc_test = [0, 8.5, 20.1, 25.5, 22.1, 14.2, 9.5, 3.8, 1.2, 0.3]

# 5. عرض النتائج والرسوم البيانية
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📊 منحنى التركيز في البلازما (PK Curve)")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # رسم المنحنيات
    ax.plot(time, conc_ref, 'o--', label='Reference (Standard Tablet)', color='#1f77b4', linewidth=2)
    ax.plot(time, conc_test, 's-', label='Test (Enhanced Formulation)', color='#2ca02c', linewidth=2)
    
    # تنسيق الرسم البياني
    ax.set_xlabel("Time (Hours)", fontsize=12)
    ax.set_ylabel("Concentration (μg/mL)", fontsize=12)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)

with col2:
    st.subheader("📉 نتائج التحليل الرقمي")
    
    # حساب AUC باستخدام قانون شبه المنحرف
    auc_ref = np.trapz(conc_ref, time)
    auc_test = np.trapz(conc_test, time)
    
    # حساب Cmax
    cmax_ref = max(conc_ref)
    cmax_test = max(conc_test)
    
    # عرض البطاقات الرقمية
    st.metric("أقصى تركيز للتركيبة المطورة (Cmax)", f"{cmax_test} μg/mL", 
              delta=f"{((cmax_test/cmax_ref)-1)*100:.1f}% أسرع")
    
    st.metric("الإتاحة الحيوية الإجمالية (AUC)", f"{auc_test:.2f}", 
              delta=f"{((auc_test/auc_ref)-1)*100:.1f}% كفاءة")
    
    st.divider()
    st.warning("⚠️ ملاحظة: هذه النتائج مبنية على محاكاة رقمية لأغراض العرض (Demo).")

# 6. التقرير النهائي
st.divider()
if auc_test > (0.8 * auc_ref) and auc_test < (1.25 * auc_ref):
    st.success("✅ النتيجة: التركيبتان تقعان ضمن نطاق التكافؤ الحيوي (Bioequivalent).")
else:
    st.error("❌ النتيجة: يوجد فرق معنوي في الإتاحة الحيوية، التركيبة المطورة تتفوق في سرعة الامتصاص.")

# زر تحميل التقرير (شكلي للمعاينة)
st.button("📥 تحميل التقرير الفني لشركة الأدوية (PDF)")
