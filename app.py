import streamlit as st
import pandas as pd
from data_utils import load_data
from filters import apply_sidebar_filters
from file_manager import handle_file_upload, show_file_list

st.set_page_config(page_title="Leebroid Dashboard", layout="wide")

# --- USER CREDENTIALS ---
USER_CREDENTIALS = {
    "kapil": {"name": "kapil", "password": "kapil123"},
    "admin": {"name": "Admin", "password": "admin123"},
}

# --- LOGIN SESSION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

if not st.session_state.authenticated:
    st.title("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
    if login_btn:
        user = USER_CREDENTIALS.get(username)
        if user and password == user["password"]:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {user['name']}!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()


# --- DASHBOARD ---

# Columns to display
COLUMNS_TO_SHOW = [
    "Customer Name", "Mobile", "Tracking Number", "Pincode", "Order Date",
    "Courier", "Product", "Payment Type", "Quantity", "Current Status", "Price"
]

# Load data
df = load_data(COLUMNS_TO_SHOW)

# Apply filters
filtered_df = apply_sidebar_filters(df)

# --- LOGOUT BUTTON ---

st.sidebar.success(f"Logged in as: {st.session_state.username}")
st.sidebar.button("🔓 Logout", on_click=lambda: st.session_state.update({"authenticated": False, "username": ""}))


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
