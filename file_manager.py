import streamlit as st
import os
import pandas as pd
from datetime import datetime

def handle_file_upload():
    uploaded_files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.markdown(f"**Preview: {uploaded_file.name}**")
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file, nrows=10)
                else:
                    df = pd.read_excel(uploaded_file, engine="openpyxl", nrows=10)
                st.dataframe(df)
            except Exception as e:
                st.warning(f"Could not preview {uploaded_file.name}: {e}")
        if st.button("Save Uploaded Files"):
            for uploaded_file in uploaded_files:
                file_path = os.path.join("data", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success("✅ Files saved successfully.")
            st.rerun()

def show_file_list():
    st.markdown("### 📄 Files in /data folder")
    existing_files = sorted([f for f in os.listdir("data") if f.endswith(('.csv', '.xlsx'))])
    if existing_files:
        for file in existing_files:
            file_path = os.path.join("data", file)
            timestamp = os.path.getmtime(file_path)
            uploaded_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            col1, col2, col3 = st.columns([5, 2, 1])
            with col1:
                st.markdown(f"📄 **{file}**")
            with col2:
                st.markdown(f"🕒 Uploaded: **{uploaded_time}**")
            with col3:
                if st.button("❌", key=f"delete_{file}"):
                    os.remove(file_path)
                    st.rerun()
    else:
        st.info("No files currently available in the data folder.")
