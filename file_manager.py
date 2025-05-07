import streamlit as st
import os
from datetime import datetime

def handle_file_upload():
    uploaded_files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join("data", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.experimental_rerun()

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
                    st.experimental_rerun()
    else:
        st.info("No files currently available in the data folder.")
