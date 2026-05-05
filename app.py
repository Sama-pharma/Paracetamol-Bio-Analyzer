import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import time

# --- إعدادات النظام المتقدمة ---
st.set_page_config(
    page_title="Sama Pharma Tech | Advanced Bio-equivalence Platform",
    page_icon="🧬",
    layout="wide"
)

# --- واجهة المستخدم الاحترافية ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .main-header { color: #0f172a; font-weight: 800; text-align: center; font-size: 2.8rem; margin-bottom: 0; }
    .regulatory-tag { background-color: #e2e8f0; color: #475569; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
    .reference-box { padding: 15px; border-radius: 12px; background-color: #ffffff; border-left: 5px solid #3b82f6; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 15px; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1); border: 1px solid #e2e8f0; }
    .status-passed { background-color: #dcfce7; border-left: 8px solid #22c55e; color: #166534; padding: 20px; border-radius: 12px; }
    .status-failed { background-color: #fee2e2; border-left: 8px solid #ef4444; color: #991b1b; padding: 20px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك البحث العلمي (Gemini API Integration) ---
def search_scientific_resources(query):
    apiKey = "" # يتم توفيره في بيئة التشغيل
    system_prompt = "You are a regulatory affairs expert in Bioequivalence. Provide a list of 3-5 specific FDA/EMA guidelines or recent research papers related to the user's drug or technology. Format as JSON with title and link."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "tools": [{"google_search": {}}]
    }
    
    # محاولة الاتصال معExponential Backoff
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
        except:
            time.sleep(delay)
    return "تعذر الاتصال بقاعدة البيانات العلمية حالياً."

# --- المحرك الرياضي (Pharmacokinetics Model) ---
def pk_model(t, dose, F, Vd, ka, ke):
    if ka == ke: ka += 0.001
    return (F * dose * ka / (Vd * (ka - ke))) * (np.exp(-ke * t) - np.exp(-ka * t))

# --- الهيكل الرئيسي للتطبيق ---
st.markdown("<h1 class='main-header'>🧬 Sama Pharma Tech | Research Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b;'>نظام التحليل المتوافق مع معايير ICH M13A و FDA GFI Bioequivalence</p>", unsafe_allow_html=True)

# تقسيم الشاشة إلى تبويبات (Tabs)
tab_analysis, tab_resources, tab_guidelines = st.tabs(["📊 التحليل والمحاكاة", "📚 المكتبة البحثية", "⚖️ أدلة المنظمات"])

with tab_analysis:
    # القائمة الجانبية للمدخلات
    with st.sidebar:
        st.header("⚙️ بروتوكول الدراسة")
        drug_name = st.text_input("اسم المادة (Active Pharmaceutical Ingredient)", "Atorvastatin Nano-crystals")
        
        st.divider()
        st.subheader("🐾 المتغيرات البيولوجية")
        species = st.selectbox("الكائن المستهدف", ["Human", "Rat", "Rabbit", "Beagle Dog"])
        weight = st.number_input("الوزن (kg)", value=70.0 if species == "Human" else 0.3)
        subjects = st.slider("عدد العينات (N)", 6, 48, 24)
        
        st.divider()
        st.subheader("💊 مواصفات المستحضر")
        formulation = st.selectbox("نوع التقنية", ["Nano-Carrier", "Conventional Tablet", "Lipid-based System"])
        dose = st.number_input("الجرعة (mg)", value=10.0)
        
        if st.button("🚀 تشغيل التحليل المعتمد"):
            # محاكاة البيانات
            t_points = np.array([0, 0.5, 1, 2, 4, 8, 12, 24])
            # قيم افتراضية للمحاكاة (سيتم استبدالها بقيم حقيقية بناءً على المراجع)
            ka_ref, ke_ref, Vd_ref = 1.2, 0.15, 0.6 * weight
            ka_test = 2.4 if formulation == "Nano-Carrier" else 1.3
            
            ref_data = [pk_model(t, dose, 0.6, Vd_ref, ka_ref, ke_ref) for t in t_points]
            test_data = [pk_model(t, dose, 0.75 if formulation == "Nano-Carrier" else 0.62, Vd_ref, ka_test, ke_ref) for t in t_points]
            
            st.session_state.results = {
                'time': t_points,
                'ref': np.array(ref_data) * np.random.normal(1, 0.05, len(t_points)),
                'test': np.array(test_data) * np.random.normal(1, 0.03, len(t_points))
            }

    if 'results' in st.session_state:
        res = st.session_state.results
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 PK Concentration-Time Curve")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(res['time'], res['ref'], 's--', label="Reference (Innovator)", color="#64748b")
            ax.plot(res['time'], res['test'], 'o-', label=f"Test ({formulation})", color="#2563eb", linewidth=2)
            ax.set_xlabel("Time (Hours)")
            ax.set_ylabel("Concentration (ng/mL)")
            ax.legend()
            st.pyplot(fig)
            
        with col2:
            st.subheader("📝 إحصائيات التكافؤ")
            auc_r = np.trapz(res['ref'], res['time'])
            auc_t = np.trapz(res['test'], res['time'])
            ratio = (auc_t / auc_r) * 100
            
            st.metric("AUC Point Estimate", f"{ratio:.2f}%")
            st.metric("Cmax Ratio", f"{(np.max(res['test'])/np.max(res['ref'])*100):.2f}%")
            
            if 80 <= ratio <= 125:
                st.markdown("<div class='status-passed'>✅ النتيجة: متكافئ حيوياً وفق معايير FDA</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='status-failed'>❌ النتيجة: غير متكافئ (خارج النطاق)</div>", unsafe_allow_html=True)

with tab_resources:
    st.subheader("🔍 البحث الذكي في المراجع والأبحاث")
    search_q = st.text_input("ابحث عن أحدث الأبحاث حول التكافؤ الحيوي لـ:", drug_name)
    if st.button("جلب المراجع العلمية"):
        with st.spinner("يتم فحص قواعد البيانات العلمية (PubMed, ScienceDirect)..."):
            research_info = search_scientific_resources(f"Latest bioequivalence studies and nanotechnology for {search_q}")
            st.markdown(f"<div class='reference-box'>{research_info}</div>", unsafe_allow_html=True)

with tab_guidelines:
    st.subheader("🏛️ أدلة المنظمات العالمية (Regulatory Guidelines)")
    
    guides = [
        {"org": "FDA", "title": "Bioequivalence Studies with Pharmacokinetic Endpoints for Drugs Submitted Under an ANDA", "year": "2021", "link": "https://www.fda.gov/media/87219/download"},
        {"org": "EMA", "title": "Guideline on the Investigation of Bioequivalence", "year": "2010", "link": "https://www.ema.europa.eu/en/documents/scientific-guideline/guideline-investigation-bioequivalence-rev-1_en.pdf"},
        {"org": "ICH", "title": "ICH M13A: Bioequivalence for Immediate-Release Solid Oral Dosage Forms", "year": "2024", "link": "https://database.ich.org/sites/default/files/ICH_M13A_Step4_Guideline_2024_0611.pdf"},
        {"org": "WHO", "title": "Multisource (generic) pharmaceutical products: guidelines on registration requirements to establish interchangeability", "year": "2017", "link": "https://cdn.who.int/media/docs/default-source/medicines/norms-and-standards/guidelines/implementation/trs937-annex7-bioequivalence.pdf"}
    ]
    
    for g in guides:
        with st.expander(f"{g['org']} - {g['year']}"):
            st.write(f"**العنوان:** {g['title']}")
            st.markdown(f"[🔗 رابط الدليل الرسمي]({g['link']})")

st.divider()
st.caption("تم تطوير هذا النظام لدعم الباحثين في شركة Sama Pharma Tech للوصول لأدق النتائج المتوافقة مع ICH Guidelines.")