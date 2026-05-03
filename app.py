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
    st.header("📂 1. Study Metadata")
    study_id = st.text_input("Protocol ID / Study ID", "SPT-BIO-2024-001")
    animal_species = st.selectbox("Species", ["Rats", "Mice", "Rabbits", "Dogs", "Humans", "Others"])
    subject_count = st.number_input("Number of Subjects (n)", min_value=1, value=6)
    avg_weight = st.number_input("Average Weight (kg/g)", min_value=0.0, value=0.25, step=0.01)
    dose_level = st.number_input("Dose Level (mg/kg)", min_value=0.0, value=10.0)
    admin_route = st.text_input("Route of Administration", "Oral Gavage")
    
    st.divider()
    st.header("📊 2. Data Upload")
    uploaded_file = st.file_uploader("Upload PK Data (Excel or CSV)", type=['xlsx', 'csv'])
    
    st.divider()
    st.header("⚙️ 3. Regulatory Settings")
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

if uploaded_file is not None:
    try:
        # قراءة البيانات المرفوعة
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Study {study_id} data loaded successfully.")
        
        # عرض ملخص بيانات التجربة
        st.info(f"📋 **Summary:** {animal_species} | Weight: {avg_weight} | Dose: {dose_level} mg/kg | Route: {admin_route}")
        
        # تقسيم الشاشة إلى قسمين: الرسم البياني والإحصائيات
        col_plot, col_stats = st.columns([2, 1])
        
        with col_plot:
            st.subheader("📊 Pharmacokinetic Profile (Linear)")
            fig, ax = plt.subplots(figsize=(10, 6))
            time_col = 'Time'
            
            if time_col in df.columns:
                pk_cols = [c for c in df.columns if c != time_col]
                for col in pk_cols:
                    ax.plot(df[time_col], df[col], 'o-', label=col, linewidth=2.5)
                
                ax.set_xlabel("Time (Hours)")
                ax.set_ylabel("Concentration (μg/mL)")
                ax.legend()
                ax.grid(True, which="both", ls="-", alpha=0.5)
                st.pyplot(fig)
                
                # خيار عرض المنحنى اللوغاريتمي (مهم للمراجعة العلمية)
                if st.checkbox("Show Semi-log Plot (For Elimination Phase)"):
                    fig2, ax2 = plt.subplots(figsize=(10, 4))
                    for col in pk_cols:
                        ax2.semilogy(df[time_col], df[col], 's-', label=col)
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
                
                pk_results[col] = {'AUC': auc, 'Cmax': cmax, 'Tmax': tmax, 'Thalf': t_half}
                
                with st.expander(f"Parameters: {col}", expanded=True):
                    st.write(f"**Cmax:** {cmax:.2f}")
                    st.write(f"**Tmax:** {tmax:.2f} h")
                    st.write(f"**AUC(0-t):** {auc:.2f}")
                    st.write(f"**t½ (Half-life):** {t_half:.2f} h")

            # حساب التكافؤ الحيوي إذا وجد دواءين للمقارنة
            if len(pk_cols) >= 2:
                st.divider()
                st.subheader("⚖️ Bioequivalence Assessment")
                test = pk_cols[-1]  # نفترض أن الأخير هو التجريبي
                ref = pk_cols[0]    # نفترض أن الأول هو المرجعي
                
                ratio_auc = (pk_results[test]['AUC'] / pk_results[ref]['AUC']) * 100
                ratio_cmax = (pk_results[test]['Cmax'] / pk_results[ref]['Cmax']) * 100
                
                # دالة التحقق من حدود التكافؤ
                def check_be(val):
                    return "✅ Passed" if be_lower <= val <= be_upper else "❌ Failed"

                st.write(f"**AUC Ratio (T/R):** {ratio_auc:.2f}% ({check_be(ratio_auc)})")
                st.write(f"**Cmax Ratio (T/R):** {ratio_cmax:.2f}% ({check_be(ratio_cmax)})")
                
                if check_be(ratio_auc) == "✅ Passed" and check_be(ratio_cmax) == "✅ Passed":
                    st.balloons()
                    st.success("The formulation is officially BIOEQUIVALENT.")
                else:
                    st.error("The formulation is NOT BIOEQUIVALENT.")

        # تجهيز البيانات للتصدير في ملف تقرير شامل
        export_data = []
        for col, val in pk_results.items():
            val_full = val.copy()
            val_full['Formulation'] = col
            val_full['Study_ID'] = study_id
            val_full['Species'] = animal_species
            val_full['Weight'] = avg_weight
            val_full['Dose'] = dose_level
            val_full['Route'] = admin_route
            export_data.append(val_full)
            
        final_df = pd.DataFrame(export_data)
        st.download_button(
            label="📥 Download Full Regulatory Report",
            data=final_df.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"{study_id}_Final_Report.csv",
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"Analysis Error: {e}")
else:
    # واجهة الترحيب في حالة عدم رفع ملف
    st.info("👋 Welcome! Please fill the Study Metadata and upload your concentration-time file to begin.")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Pharmacokinetics_curve.svg/640px-Pharmacokinetics_curve.svg.png", caption="Standard PK Profile Visualization")

st.divider()
st.caption(f"Sama Pharma Tech | Digital Bioequivalence Suite | Protocol Tracking: {study_id} | © 2024")