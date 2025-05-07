import os
import pandas as pd

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
        "Current Status": "Current Status"
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
            df = shiprocket_column_mapping(df)
        elif file.endswith(".xlsx"):
            df = pd.read_excel(path, engine="openpyxl", header=1)
            df = delhivery_column_mapping(df)
            df["Courier"] = "Delhivery"
        else:
            continue
        dfs.append(df)

    if not dfs:
        return pd.DataFrame(columns=columns_to_show)

    full_df = pd.concat(dfs, ignore_index=True)
    for col in columns_to_show:
        if col not in full_df.columns:
            full_df[col] = None
    return full_df[columns_to_show].copy()
