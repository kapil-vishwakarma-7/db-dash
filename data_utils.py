import os
import pandas as pd
import re


def extract_quantity(description):
    if isinstance(description, str):
        match = re.search(r"\((\d+)\)$", description.strip())
        if match:
            return int(match.group(1))
    return 1  # Default quantity if not found


def shiprocket_column_mapping(df):
    mapping = {
        "Order ID": "Tracking Number",
        "Customer Mobile": "Mobile",
        "Product Name": "Product",
        "Shiprocket Created At": "Order Date",
        "Customer Name": "Customer Name",
        "Courier Company": "Courier",
        "Address Pincode": "Pincode",
        "Product Quantity": "Quantity",
        "Order Total": "Price",
        "Address Line 1" : "Full Address",
        "Address City" : "City",
        "Status": "Current Status",
        "Payment Method" : "Payment Type"
    }
    return df.rename(columns=mapping)

def delhivery_column_mapping(df):
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
        "Type": "Payment Type",
        "Current Status": "Current Status",
        "City" : "City"
    }
    return df.rename(columns=mapping)

def get_current_files():
    return sorted([f for f in os.listdir("data") if f.endswith(('.csv', '.xlsx'))])

def load_data(columns_to_show):
    dfs = []
    for file in get_current_files():
        path = os.path.join("data", file)
        if file.endswith(".csv"):
            df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip", header=0)
            if "Shiprocket" in file:
                df = shiprocket_column_mapping(df)
            else: 
                df = delhivery_column_mapping(df)
                if "Product" in df.columns:
                    df["Quantity"] = df["Product"].apply(extract_quantity)
        elif file.endswith(".xlsx"):
            df = pd.read_excel(path, engine="openpyxl", header=1)
            df = delhivery_column_mapping(df)
            df["Courier"] = "Delhivery"
        else:
            continue
        # Strip column headers
        df.columns = df.columns.str.strip()
        # Normalize and parse date
        if "Order Date" in df.columns:
            df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
        

        dfs.append(df)
        


    if not dfs:
        return pd.DataFrame(columns=columns_to_show)

    full_df = pd.concat(dfs, ignore_index=True)
    for col in columns_to_show:
        if col not in full_df.columns:
            full_df[col] = None
    return full_df[columns_to_show].copy()
