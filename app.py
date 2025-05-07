import streamlit as st
import pandas as pd
import os
from datetime import datetime


st.set_page_config(page_title="Leebroid Dashboard", layout="wide")



import streamlit as st

# --- USER CREDENTIALS (hardcoded or load from file) ---
USER_CREDENTIALS = {
    "kapil": {
        "name": "Kapil",
        "password": "kapil123"
    },
    "admin": {
        "name": "Admin",
        "password": "admin123"
    }
}

# --- AUTHENTICATION LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
else:
    # Do not overwrite the value — keep existing session
    pass


if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
    
    if login_btn:
        user = USER_CREDENTIALS.get(username)
        if user and password == user["password"]:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.balloons()
            st.success(f"🎉 Welcome, {user['name']}!")

            st.rerun()
        else:
            st.error("❌ Invalid username or password.")
    st.stop()








# --- APP STATE ---
if "loaded_files" not in st.session_state:
    st.session_state["loaded_files"] = []
if "df" not in st.session_state:
    st.session_state["df"] = None




# Initialize session state to avoid infinite rerun
if "data_uploaded" not in st.session_state:
    st.session_state["data_uploaded"] = False



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

# Helpers
def get_current_files():
    return sorted([f for f in os.listdir("data") if f.endswith(('.csv', '.xlsx'))])




def infer_courier_label(filename):
    fname = filename.lower()
    if "delhivery" in fname:
        return "Delhivery"
    elif "shiprocket" in fname:
        return "Shiprocket"
    elif "post" in fname:
        return "Post Office"
    else:
        return "Unknown"

# Load and normalize data from multiple files
# @st.cache_data(ttl=0)
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

# Only run load_data after rerun triggered
df = load_data()
if st.session_state["data_uploaded"]:
    st.session_state["data_uploaded"] = False

# Unique values for dropdowns
product_options = df["Current Status"].dropna().unique().tolist()



# Sidebar filters
st.sidebar.header("🔍 Search Orders")

filtered_df = df.copy()

# 🗓️ Order Date filter first
if "Order Date" in filtered_df.columns:
    filtered_df["Order Date"] = pd.to_datetime(filtered_df["Order Date"], errors="coerce")
    min_date = filtered_df["Order Date"].min()
    max_date = filtered_df["Order Date"].max()
    date_range = st.sidebar.date_input("📅 Order Date Range", [min_date, max_date])
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["Order Date"] >= pd.to_datetime(start_date)) &
            (filtered_df["Order Date"] <= pd.to_datetime(end_date))
        ]

# Other filters
name_filter = st.sidebar.text_input("Customer Name")
mobile_filter = st.sidebar.text_input("Mobile Number")
tracking_filter = st.sidebar.text_input("Tracking Number")
pincode_filter = st.sidebar.text_input("Pincode")
status_filter = st.sidebar.selectbox("Current Status", ["All"] + df["Current Status"].dropna().unique().tolist())

if name_filter:
    filtered_df = filtered_df[filtered_df["Customer Name"].astype(str).str.contains(name_filter, case=False, na=False)]
if mobile_filter:
    filtered_df = filtered_df[filtered_df["Mobile"].astype(str).str.contains(mobile_filter)]
if tracking_filter:
    filtered_df = filtered_df[filtered_df["Tracking Number"].astype(str).str.contains(tracking_filter)]
if pincode_filter:
    filtered_df = filtered_df[filtered_df["Pincode"].astype(str).str.contains(pincode_filter)]
if status_filter != "All":
    filtered_df = filtered_df[filtered_df["Current Status"] == status_filter]


# --- LOGOUT BUTTON ---

st.sidebar.success(f"Logged in as: {st.session_state.username}")
st.sidebar.button("🔓 Logout", on_click=lambda: st.session_state.update({"authenticated": False, "username": ""}))

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
    st.write(f"###### 🧾 {len(filtered_df)} matching orders")
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
            file_path = os.path.join("data", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
    
        st.session_state["df"] = None
        st.session_state["loaded_files"] = []
        st.rerun()

    st.markdown("### 📄 Files in /data folder")
    existing_files = get_current_files()
    if existing_files:
        
        for file in existing_files:
            file_path = os.path.join("data", file)
            col1, col2, col3 = st.columns([5, 2, 1])
            with col1:
                st.markdown(f"📄 **{file}**")
            with col2:
                if os.path.exists(file_path):
                    timestamp = os.path.getmtime(file_path)
                    uploaded_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    st.markdown(f"**{uploaded_time}**")
                else:
                    st.markdown("Uploaded: Unknown")
            with col3:
                if st.button("❌", key=f"delete_{file}"):
                    os.remove(os.path.join("data", file))
                    st.session_state["df"] = None
                    st.session_state["loaded_files"] = []
                    st.rerun()
    else:
        st.info("No files currently available in the data folder.")
