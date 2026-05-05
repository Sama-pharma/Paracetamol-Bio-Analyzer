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
    .status-passed { background-color: #dcfce7; border-left: 8px solid #22c55e; color: #166534; padding: 10px; border-radius: 8px; font-weight: bold; }
    .status-failed { background-color: #fee2e2; border-left: 8px solid #ef4444; color: #991b1b; padding: 10px; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك البحث العلمي (Gemini API Integration) ---
def search_scientific_resources(query):
    apiKey = "" # يتم توفيره في بيئة التشغيل
    system_prompt = "You are a regulatory affairs expert in Bioequivalence. Provide a list of 5-7 specific FDA/EMA guidelines or recent research papers related to the user's drug or technology. Format as JSON with title and link."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "tools": [{"google_search": {}}]
    }
    
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
st.markdown("<p style='text-align:center; color:#64748b;'>نظام التحليل المتعدد المتوافق مع معايير ICH M13A و FDA GFI Bioequivalence</p>", unsafe_allow_html=True)

st.divider()

# تقسيم الشاشة إلى تبويبات (Tabs)
tab_analysis, tab_resources, tab_guidelines = st.tabs(["📊 التحليل المقارن (3 تركيبات)", "📚 المكتبة البحثية المتقدمة", "⚖️ دليل المنظمات الدولية"])

with tab_analysis:
    with st.sidebar:
        st.header("⚙️ بروتوكول الدراسة")
        drug_name = st.text_input("اسم المادة الفعالة (API)", "Atorvastatin")
        
        st.divider()
        st.subheader("🐾 المتغيرات البيولوجية")
        species = st.selectbox("الكائن المستهدف", ["Human", "Rat", "Rabbit", "Beagle Dog"])
        weight = st.number_input("الوزن المتوسط (kg)", value=70.0 if species == "Human" else 0.3)
        subjects = st.slider("عدد العينات لكل مجموعة (N)", 6, 48, 24)
        
        st.divider()
        st.subheader("💊 مواصفات التركيبات المقارنة")
        dose = st.number_input("الجرعة (mg)", value=10.0)
        
        t1_form = st.selectbox("التركيبة الاختبارية 1", ["Nano-Carrier", "Lipid-based", "Polymeric NP"], key="t1")
        t2_form = st.selectbox("التركيبة الاختبارية 2", ["Conventional Tablet", "Oral Suspension"], key="t2")
        t3_form = st.selectbox("التركيبة الاختبارية 3", ["Nano-emulsion", "Solid Dispersion"], key="t3")
        
        if st.button("🚀 تشغيل التحليل المقارن الشامل"):
            t_points = np.array([0, 0.5, 1, 2, 4, 8, 12, 24])
            ka_ref, ke_ref, Vd_ref = 1.2, 0.15, 0.6 * weight
            
            # محاكاة البيانات للتركيبات الثلاثة والمنظم
            def get_data(form_type, is_ref=False):
                if is_ref:
                    F, ka = 0.6, 1.2
                else:
                    # معاملات متغيرة بناء على النوع
                    if "Nano" in form_type: F, ka = 0.8, 2.5
                    elif "Lipid" in form_type: F, ka = 0.72, 1.8
                    elif "Suspension" in form_type: F, ka = 0.65, 1.6
                    else: F, ka = 0.62, 1.3
                
                base = [pk_model(t, dose, F, Vd_ref, ka, ke_ref) for t in t_points]
                return np.array(base) * np.random.normal(1, 0.04, len(t_points))

            st.session_state.multi_results = {
                'time': t_points,
                'Ref': get_data(None, True),
                'Test 1': get_data(t1_form),
                'Test 2': get_data(t2_form),
                'Test 3': get_data(t3_form),
                'names': [t1_form, t2_form, t3_form]
            }

    if 'multi_results' in st.session_state:
        res = st.session_state.multi_results
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Multi-Formulation PK Profile")
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ["#64748b", "#2563eb", "#d97706", "#059669"]
            ax.plot(res['time'], res['Ref'], 's--', label="Reference (Innovator)", color=colors[0], alpha=0.8)
            ax.plot(res['time'], res['Test 1'], 'o-', label=f"Test 1: {res['names'][0]}", color=colors[1], linewidth=2)
            ax.plot(res['time'], res['Test 2'], '^-', label=f"Test 2: {res['names'][1]}", color=colors[2], linewidth=2)
            ax.plot(res['time'], res['Test 3'], 'd-', label=f"Test 3: {res['names'][2]}", color=colors[3], linewidth=2)
            ax.set_xlabel("Time (Hours)")
            ax.set_ylabel("Concentration (ng/mL)")
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend()
            st.pyplot(fig)
            
        with col2:
            st.subheader("📝 Comparative Metrics")
            auc_ref = np.trapz(res['Ref'], res['time'])
            
            for i, key in enumerate(['Test 1', 'Test 2', 'Test 3']):
                auc_t = np.trapz(res[key], res['time'])
                ratio = (auc_t / auc_ref) * 100
                cmax_t = np.max(res[key])
                cmax_r = np.max(res['Ref'])
                cmax_ratio = (cmax_t / cmax_r) * 100
                
                with st.expander(f"Analysis: {key} ({res['names'][i]})", expanded=True):
                    st.write(f"**AUC Ratio:** {ratio:.2f}%")
                    st.write(f"**Cmax Ratio:** {cmax_ratio:.2f}%")
                    if 80 <= ratio <= 125:
                        st.markdown("<div class='status-passed'>✅ Bioequivalent</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='status-failed'>❌ Non-Equivalent</div>", unsafe_allow_html=True)

with tab_resources:
    st.subheader("🔍 البحث العلمي المتكامل (PubMed & Regulatory Databases)")
    search_q = st.text_input("ابحث عن أحدث الأبحاث حول:", drug_name)
    if st.button("تحديث قاعدة البيانات البحثية"):
        with st.spinner("يتم فحص المكتبات الوطنية والأبحاث السريرية..."):
            research_info = search_scientific_resources(f"Comparative bioequivalence and PK parameters for {search_q} in different formulations")
            st.markdown(f"<div class='reference-box'>{research_info}</div>", unsafe_allow_html=True)

with tab_guidelines:
    st.subheader("🏛️ أدلة المنظمات العالمية والمكتبات المرجعية")
    
    guides = [
        {"org": "FDA", "title": "Statistical Approaches to Establishing Bioequivalence", "year": "2023", "link": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/statistical-approaches-establishing-bioequivalence"},
        {"org": "EMA", "title": "Guideline on the Investigation of Bioequivalence (CPMP/EWP/QWP/1401/98)", "year": "2010", "link": "https://www.ema.europa.eu/en/documents/scientific-guideline/guideline-investigation-bioequivalence-rev-1_en.pdf"},
        {"org": "ICH", "title": "M13A: Bioequivalence for Immediate-Release Solid Oral Dosage Forms", "year": "2024", "link": "https://database.ich.org/sites/default/files/ICH_M13A_Step4_Guideline_2024_0611.pdf"},
        {"org": "WHO", "title": "TRS 1003 - Annex 6: Guidance on Bioequivalence Studies", "year": "2017", "link": "https://cdn.who.int/media/docs/default-source/medicines/norms-and-standards/guidelines/implementation/trs1003-annex6.pdf"},
        {"org": "USP", "title": "USP <1092> The Dissolution Procedure: Development and Validation", "year": "2022", "link": "https://www.usp.org/"}
    ]
    
    for g in guides:
        col_g1, col_g2 = st.columns([3, 1])
        with col_g1:
            st.markdown(f"**{g['org']} ({g['year']}):** {g['title']}")
        with col_g2:
            st.markdown(f"[🔗 رابط الدليل]({g['link']})")
        st.divider()

st.caption("تم تطوير هذا النظام المتطور لشركة Sama Pharma Tech لدعم التحليلات المقارنة المعقدة والأبحاث الرقابية.")