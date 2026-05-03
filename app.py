import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# إعدادات الصفحة الرسمية
st.set_page_config(
    page_title="Sama Pharma Tech | Regulatory Bio-Analyzer",
    page_icon="💊",
    layout="wide"
)

# تنسيق الواجهة (CSS) لتحسين المظهر وجعل الخطوط واضحة
st.markdown("""
    <style>
    .main { text-align: left; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; color: #1E88E5; }
    .stHeader { color: #0D47A1; }
    .success-box { padding: 10px; border-radius: 5px; background-color: #e8f5e9; border: 1px solid #2e7d32; }
    .warning-box { padding: 10px; border-radius: 5px; background-color: #fff3e0; border: 1px solid #ef6c00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔬 Full Bioequivalence & PK Analysis Platform")
st.subheader("Sama Pharma Tech | Regulatory Compliance Suite")

st.divider()

# القائمة الجانبية لإدخال بيانات الدراسة (Metadata)
with st.sidebar:
    st.header("📂 1. Study & Drug Information")
    study_id = st.text_input("Protocol ID / Study ID", "SPT-BIO-2024-001")
    drug_name = st.text_input("Active Pharmaceutical Ingredient (API)", "Paracetamol")
    
    st.subheader("🧪 Test Formulation Details")
    test_brand = st.text_input("Test Product Name", "Sama-Cetamol (Test)")
    test_batch = st.text_input("Test Batch No.", "T-2024-001")
    test_strength = st.text_input("Test Strength", "500 mg")

    st.subheader("💊 Reference Formulation Details")
    ref_brand = st.text_input("Reference Product Name", "Panadol (Reference)")
    ref_batch = st.text_input("Reference Batch No.", "R-2024-999")
    ref_strength = st.text_input("Reference Strength", "500 mg")

    st.divider()
    st.header("🐾 2. Subject Information")
    animal_species = st.selectbox("Species", ["Rats", "Mice", "Rabbits", "Dogs", "Humans", "Others"])
    subject_count = st.number_input("Number of Subjects (n)", min_value=1, value=6)
    avg_weight = st.number_input("Average Weight (kg/g)", min_value=0.0, value=0.25, step=0.01)
    dose_level = st.number_input("Dose Level (mg/kg)", min_value=0.0, value=10.0)
    admin_route = st.text_input("Route of Administration", "Oral Gavage")
    
    st.divider()
    st.header("📊 3. Data Management")
    uploaded_file = st.file_uploader("Upload PK Data (Excel or CSV)", type=['xlsx', 'csv'])
    
    # ميزة تجريبية: زر لتحميل بيانات افتراضية لأي دواء للتجربة
    if st.button("🚀 Load Sample Drug Data"):
        sample_data = {
            'Time': [0, 0.5, 1, 1.5, 2, 4, 8, 12, 24],
            'Reference_Drug': [0, 15.2, 28.4, 32.1, 29.5, 18.2, 8.4, 3.1, 0.5],
            'Test_Formulation': [0, 14.8, 27.9, 31.5, 30.1, 19.5, 9.2, 3.8, 0.6]
        }
        uploaded_file = pd.DataFrame(sample_data)
        st.success("Sample data loaded for testing.")
    
    st.divider()
    st.header("⚙️ 4. Regulatory Settings")
    st.write("Bioequivalence Limits (Global Standards)")
    be_lower = st.number_input("Lower Limit (%)", value=80.0)
    be_upper = st.number_input("Upper Limit (%)", value=125.0)

# دالة حساب المساحة تحت المنحنى (AUC)
def calculate_auc(time, conc):
    return np.trapz(conc, time)

# دالة تقدير وقت نصف العمر (t1/2) بناءً على المرحلة النهائية
def calculate_half_life(time, conc):
    try:
        # استخدام آخر 3 نقاط لتقدير معدل التخلص (Elimination phase)
        log_conc = np.log(conc[-3:]) 
        slope, _ = np.polyfit(time[-3:], log_conc, 1)
        ke = -slope
        return 0.693 / ke if ke > 0 else 0
    except:
        return 0

# معالجة البيانات سواء كانت مرفوعة أو تجريبية
df = None
if uploaded_file is not None:
    if isinstance(uploaded_file, pd.DataFrame):
        df = uploaded_file
    elif uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

if df is not None:
    try:
        st.success(f"✅ Study {study_id} data is active.")
        
        # عرض ملخص بيانات التجربة والدواء
        st.info(f"""
        💊 **Drug:** {drug_name} | **Protocol:** {study_id}
        \n🔍 **Test:** {test_brand} ({test_strength}) | **Ref:** {ref_brand} ({ref_strength})
        \n📋 **Subjects:** {animal_species} (n={subject_count}) | Dose: {dose_level} mg/kg | Route: {admin_route}
        """)
        
        # تقسيم الشاشة إلى قسمين: الرسم البياني والإحصائيات
        col_plot, col_stats = st.columns([2, 1])
        
        with col_plot:
            st.subheader("📊 Pharmacokinetic Profile (Linear)")
            fig, ax = plt.subplots(figsize=(10, 6))
            time_col = 'Time'
            
            if time_col in df.columns:
                pk_cols = [c for c in df.columns if c != time_col]
                for col in pk_cols:
                    label_name = test_brand if "Test" in col else ref_brand
                    ax.plot(df[time_col], df[col], 'o-', label=label_name, linewidth=2.5)
                
                ax.set_xlabel("Time (Hours)")
                ax.set_ylabel("Concentration (μg/mL)")
                ax.legend()
                ax.grid(True, which="both", ls="-", alpha=0.5)
                st.pyplot(fig)
                
                # خيار عرض المنحنى اللوغاريتمي
                if st.checkbox("Show Semi-log Plot (For Elimination Phase)"):
                    fig2, ax2 = plt.subplots(figsize=(10, 4))
                    for col in pk_cols:
                        label_name = test_brand if "Test" in col else ref_brand
                        ax2.semilogy(df[time_col], df[col], 's-', label=label_name)
                    ax2.set_ylabel("Log Concentration")
                    ax2.grid(True)
                    st.pyplot(fig2)
            
        with col_stats:
            st.subheader("📝 PK Parameters")
            pk_results = {}
            
            for col in pk_cols:
                cmax = df[col].max()
                tmax = df[df[col] == cmax][time_col].values[0]
                auc = calculate_auc(df[time_col], df[col])
                t_half = calculate_half_life(df[time_col].values, df[col].values)
                
                brand_display = test_brand if "Test" in col else ref_brand
                pk_results[col] = {
                    'Brand': brand_display,
                    'AUC': auc, 
                    'Cmax': cmax, 
                    'Tmax': tmax, 
                    'Thalf': t_half
                }
                
                with st.expander(f"Parameters: {brand_display}", expanded=True):
                    st.write(f"**Cmax:** {cmax:.2f}")
                    st.write(f"**Tmax:** {tmax:.2f} h")
                    st.write(f"**AUC(0-t):** {auc:.2f}")
                    st.write(f"**t½ (Half-life):** {t_half:.2f} h")

            # حساب التكافؤ الحيوي
            if len(pk_cols) >= 2:
                st.divider()
                st.subheader("⚖️ Bioequivalence Assessment")
                test_col = pk_cols[-1]
                ref_col = pk_cols[0]
                
                ratio_auc = (pk_results[test_col]['AUC'] / pk_results[ref_col]['AUC']) * 100
                ratio_cmax = (pk_results[test_col]['Cmax'] / pk_results[ref_col]['Cmax']) * 100
                
                def check_be(val):
                    return "✅ Passed" if be_lower <= val <= be_upper else "❌ Failed"

                st.write(f"**AUC Ratio (T/R):** {ratio_auc:.2f}% ({check_be(ratio_auc)})")
                st.write(f"**Cmax Ratio (T/R):** {ratio_cmax:.2f}% ({check_be(ratio_cmax)})")
                
                if check_be(ratio_auc) == "✅ Passed" and check_be(ratio_cmax) == "✅ Passed":
                    st.balloons()
                    st.success(f"Formulation '{test_brand}' is BIOEQUIVALENT to '{ref_brand}'.")
                else:
                    st.error(f"Formulation '{test_brand}' is NOT BIOEQUIVALENT.")

        # تصدير البيانات
        export_data = []
        for col, val in pk_results.items():
            val_full = val.copy()
            val_full['API'] = drug_name
            val_full['Study_ID'] = study_id
            val_full['Species'] = animal_species
            val_full['Dose'] = dose_level
            val_full['Route'] = admin_route
            if "Test" in col:
                val_full['Batch'] = test_batch
                val_full['Strength'] = test_strength
            else:
                val_full['Batch'] = ref_batch
                val_full['Strength'] = ref_strength
            export_data.append(val_full)
            
        final_df = pd.DataFrame(export_data)
        st.download_button(
            label="📥 Download Full Regulatory Report",
            data=final_df.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"{study_id}_{drug_name}_Report.csv",
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"Analysis Error: {e}")
else:
    st.info("👋 Welcome! Fill the Study & Drug Metadata, or click 'Load Sample Drug Data' in the sidebar to try it now.")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Pharmacokinetics_curve.svg/640px-Pharmacokinetics_curve.svg.png", caption="Standard PK Profile Visualization")

st.divider()
st.caption(f"Sama Pharma Tech | Digital Bioequivalence Suite | API: {drug_name} | © 2024")