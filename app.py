import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# Page Configuration
st.set_page_config(
    page_title="Sama Pharma Tech | Bio-Analyzer",
    page_icon="💊",
    layout="wide"
)

# Custom Styling (LTR for English)
st.markdown("""
    <style>
    .main { text-align: left; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔬 Advanced Bioequivalence Analysis Platform")
st.subheader("Sama Pharma Tech Professional Bio-Analyzer")

st.divider()

# Sidebar Configuration
with st.sidebar:
    st.header("📂 Data Management")
    uploaded_file = st.file_uploader("Upload Lab Results (Excel or CSV)", type=['xlsx', 'csv'])
    st.info("Note: The file must contain a 'Time' column and concentration columns.")
    
    st.divider()
    st.header("⚙️ Analysis Settings")
    confidence_level = st.slider("Statistical Confidence Level", 0.80, 0.99, 0.95)

# AUC Calculation Function (Trapezoidal Rule)
def calculate_auc(time, concentration):
    return np.trapz(concentration, time)

if uploaded_file is not None:
    try:
        # Read Uploaded File
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
        
        # Layout Splitting
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 Pharmacokinetic (PK) Curve")
            fig, ax = plt.subplots(figsize=(10, 6))
            
            time_col = 'Time' # Assuming column name
            if time_col in df.columns:
                columns_to_plot = [c for c in df.columns if c != time_col]
                for col in columns_to_plot:
                    ax.plot(df[time_col], df[col], 'o-', label=col, linewidth=2)
                
                ax.set_xlabel("Time (Hours)")
                ax.set_ylabel("Concentration (μg/mL)")
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig)
            else:
                st.error("Error: 'Time' column not found in the uploaded file.")

        with col2:
            st.subheader("📝 Analytical Results")
            results = []
            if time_col in df.columns:
                for col in [c for c in df.columns if c != time_col]:
                    cmax = df[col].max()
                    tmax = df[df[col] == cmax][time_col].values[0]
                    auc = calculate_auc(df[time_col], df[col])
                    
                    st.metric(f"Cmax - {col}", f"{cmax:.2f}")
                    st.metric(f"AUC - {col}", f"{auc:.2f}")
                    results.append({"Drug": col, "Cmax": cmax, "Tmax": tmax, "AUC": auc})
                    st.write("---")
            
            # Download Results Button
            res_df = pd.DataFrame(results)
            csv = res_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Download Analysis Report (CSV)", data=csv, file_name="BioAnalysis_Report.csv")

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    # Landing View
    st.info("👋 Welcome! Please upload your data file from the sidebar to begin analysis.")
    
    # Data Format Example
    st.subheader("💡 Required Data Format Example:")
    example_data = {
        'Time': [0, 0.5, 1, 2, 4, 8],
        'Reference_Drug': [0, 15, 25, 18, 10, 2],
        'Test_Drug_Nano': [0, 22, 28, 20, 9, 1]
    }
    st.table(pd.DataFrame(example_data))

st.divider()
st.caption("Developed by Sama Pharma Tech - All Rights Reserved © 2024")