import streamlit as st
import pandas as pd

def apply_sidebar_filters(df):
    filtered_df = df.copy()

    # Order Date filter
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

    name = st.sidebar.text_input("Customer Name")
    mobile = st.sidebar.text_input("Mobile Number")
    tracking = st.sidebar.text_input("Tracking Number")
    pincode = st.sidebar.text_input("Pincode")
    status_options = ["All"] + df["Current Status"].dropna().unique().tolist()
    status = st.sidebar.selectbox("Current Status", status_options)

    if name:
        filtered_df = filtered_df[filtered_df["Customer Name"].astype(str).str.contains(name, case=False, na=False)]
    if mobile:
        filtered_df = filtered_df[filtered_df["Mobile"].astype(str).str.contains(mobile)]
    if tracking:
        filtered_df = filtered_df[filtered_df["Tracking Number"].astype(str).str.contains(tracking)]
    if pincode:
        filtered_df = filtered_df[filtered_df["Pincode"].astype(str).str.contains(pincode)]
    if status != "All":
        filtered_df = filtered_df[filtered_df["Current Status"] == status]

    return filtered_df
