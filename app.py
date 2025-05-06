import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Leebroid Dashboard", layout="wide")


# Column name mapping across different files
def shiprocket_column_mapping(df):
    mapping = {
        "Waybill": "Tracking Number",
        "Customer Mobile": "Mobile",
        "Product Description": "Product",
        "Pick Up Date": "Order Date",
        "Seller Name": "Customer Name",
        "Courier Company": "Courier",
        "Pincode": "Pincode",
        "Zip": "Pincode",
        "Phone": "Mobile1",
        "Qty": "Quantity",
        "Amount": "Price"
    }
    df = df.rename(columns=mapping)
    return df

def delihvery_column_mapping(df):
    mapping = {
        "Waybill": "Tracking Number",
        "Reference No.": "Mobile",
        "Product Description": "Product",
        "Pick Up Date": "Order Date",
        "Consignee Name": "Customer Name",
        "Client": "Courier",
        "PIN": "Pincode",
        "Zip": "Pincode",
        "Phone": "Mobile1",
        "Qty": "Quantity",
        "Amount": "Price",
        "Type" : "Payment Type",
        "Current Status" : "Current Status"
    }
    df = df.rename(columns=mapping)
    return df

# Columns to display in table
COLUMNS_TO_SHOW = ["Customer Name", "Mobile", "Tracking Number", "Pincode", "Order Date", "Courier", "Product", "Payment Type", "Quantity", "Current Status", "Price"]

# Load and normalize data from multiple files
@st.cache_data
def load_data():
    dfs = []
    for file in os.listdir("data"):
        path = os.path.join("data", file)
        if file.endswith(".csv"):
            df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip", header=0)
            df = shiprocket_column_mapping(df)
        elif file.endswith(".xlsx"):
            # Use second row as header for Delhivery-style files
            df = pd.read_excel(path, engine="openpyxl", header=1)
            df = delihvery_column_mapping(df)
            df["Courier"] = "Delhivery"
        else:
            continue
        
        dfs.append(df)
    full_df = pd.concat(dfs, ignore_index=True)
    # Add missing columns if any
    for col in COLUMNS_TO_SHOW:
        if col not in full_df.columns:
            full_df[col] = None
    return full_df[COLUMNS_TO_SHOW].copy()

df = load_data()

#unique values 
product_options = df["Current Status"].dropna().unique().tolist()




# Sidebar filters
st.sidebar.header("🔍 Search Orders")
name = st.sidebar.text_input("Customer Name")
mobile = st.sidebar.text_input("Mobile Number")
tracking = st.sidebar.text_input("Tracking Number")
pincode = st.sidebar.text_input("Pincode")
selected_product = st.sidebar.selectbox("Current Status", ["All"] + product_options)


filtered_df = df.copy()
if name: filtered_df = filtered_df[filtered_df["Customer Name"].astype(str).str.contains(name, case=False, na=False)]
if mobile: filtered_df = filtered_df[filtered_df["Mobile"].astype(str).str.contains(mobile)]
if tracking: filtered_df = filtered_df[filtered_df["Tracking Number"].astype(str).str.contains(tracking)]
if pincode: filtered_df = filtered_df[filtered_df["Pincode"].astype(str).str.contains(pincode)]
if selected_product != "All":
    filtered_df = filtered_df[filtered_df["Current Status"] == selected_product]


# Header
# st.title("📦 Leebroid Order Dashboard")

# # Metric layout
# col1, col2 = st.columns(2)
# with col1:
#     st.metric("Total Orders", len(df))
# with col2:
#     st.metric("Unique Customers", df["Mobile"].nunique() if "Mobile" in df.columns else "N/A")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔎 Order Search", "📈 Daily Sales", "📁 Data Files"])

with tab1:
    st.write(f"### 🧾 {len(filtered_df)} matching orders")
    st.dataframe(filtered_df)

with tab2:
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
        summary = df.groupby(df["Order Date"].dt.date).size().reset_index(name="Total Orders")
        st.line_chart(summary.set_index("Order Date"))
    else:
        st.warning("⚠️ 'Order Date' column not found.")

# Tab 3: Data Files Management
with tab3:
    st.subheader("📁 Upload and Manage Data Files")

    uploaded_files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with open(os.path.join("data", uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} file(s) successfully.")
        st.experimental_rerun()

    st.markdown("### 📄 Files in /data folder")
    existing_files = os.listdir("data")
    if existing_files:
        for file in existing_files:
            st.markdown(f"- {file}")
    else:
        st.info("No files currently available in the data folder.")

