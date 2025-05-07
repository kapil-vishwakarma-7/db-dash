import streamlit as st
import pandas as pd
from data_utils import load_data
from filters import apply_sidebar_filters
from file_manager import handle_file_upload, show_file_list

st.set_page_config(page_title="Leebroid Dashboard", layout="wide")

# Columns to display
COLUMNS_TO_SHOW = [
    "Customer Name", "Mobile", "Tracking Number", "Pincode", "Order Date",
    "Courier", "Product", "Payment Type", "Quantity", "Current Status", "Price"
]

# Load data
df = load_data(COLUMNS_TO_SHOW)

# Apply filters
filtered_df = apply_sidebar_filters(df)

# Tabs
tab1, tab2, tab3 = st.tabs(["🔎 Order Search", "📈 Daily Sales", "📁 Data Files"])

with tab1:
    st.write(f"### 🧾 {len(filtered_df)} matching orders")
    st.dataframe(filtered_df)

with tab2:
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
        summary = df.groupby(df["Order Date"].dt.date).size().reset_index(name="Total Orders")
        st.line_chart(summary.set_index("Order Date"))
    else:
        st.warning("⚠️ 'Order Date' column not found.")

with tab3:
    st.subheader("📁 Upload and Manage Data Files")
    handle_file_upload()
    show_file_list()
