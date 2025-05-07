import streamlit as st
import pandas as pd
import plotly.express as px

def render_sales_tab(df, tab2):
    with tab2:
        st.subheader("📈 Daily Sales Overview")

        if "Order Date" in df.columns:
            df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
            df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

            # Filter by courier
            couriers = df["Courier"].dropna().unique().tolist()
            selected_courier = st.selectbox("Filter by Courier", ["All"] + couriers)
            if selected_courier != "All":
                df = df[df["Courier"] == selected_courier]

            # Filter by product
            products = df["Product"].dropna().unique().tolist()
            selected_product = st.selectbox("Filter by Product", ["All"] + products)
            if selected_product != "All":
                df = df[df["Product"] == selected_product]

            # Filter by date range
            min_date = df["Order Date"].min().date()
            max_date = df["Order Date"].max().date()
            date_range = st.date_input("Select Date Range", [min_date, max_date])
            if len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df["Order Date"].dt.date >= start_date) & (df["Order Date"].dt.date <= end_date)]

            # Grouping option
            freq = st.selectbox("Group by", ["Day", "Week", "Month"])
            if freq == "Week":
                df["GroupDate"] = df["Order Date"].dt.to_period("W").dt.start_time
            elif freq == "Month":
                df["GroupDate"] = df["Order Date"].dt.to_period("M").dt.start_time
            else:
                df["GroupDate"] = df["Order Date"].dt.date

            # Aggregation
            order_count = df.groupby("GroupDate").size().reset_index(name="Total Orders")
            revenue_summary = df.groupby("GroupDate")["Price"].sum().reset_index(name="Total Revenue")
            order_count["7d Avg"] = order_count["Total Orders"].rolling(7).mean()

            # Toggle metric
            metric_type = st.radio("Display Metric", ["Order Count", "Total Revenue", "Smoothed (7d Avg)"])
            if metric_type == "Order Count":
                fig = px.line(order_count, x="GroupDate", y="Total Orders", title="Order Count")
            elif metric_type == "Smoothed (7d Avg)":
                fig = px.line(order_count, x="GroupDate", y="7d Avg", title="Smoothed 7-Day Avg Orders")
            else:
                fig = px.bar(revenue_summary, x="GroupDate", y="Total Revenue", title="Total Revenue")
            st.plotly_chart(fig)

            # KPIs
            st.markdown("### 📊 Daily KPIs")
            col1, col2, col3 = st.columns(3)
            with col1:
                peak_day = order_count.loc[order_count["Total Orders"].idxmax()]
                st.metric("📦 Peak Order Day", str(peak_day["GroupDate"]), int(peak_day["Total Orders"]))
            with col2:
                top_revenue = revenue_summary.loc[revenue_summary["Total Revenue"].idxmax()]
                st.metric("💰 Top Revenue Day", str(top_revenue["GroupDate"]), f"{top_revenue['Total Revenue']:.2f}")
            with col3:
                avg_orders = order_count["Total Orders"].mean()
                st.metric("📈 Avg. Orders", f"{avg_orders:.1f}")

            # Cumulative Revenue
            st.markdown("### 📈 Cumulative Revenue")
            cumulative = revenue_summary.copy()
            cumulative["Cumulative"] = cumulative["Total Revenue"].cumsum()
            st.line_chart(cumulative.set_index("GroupDate")["Cumulative"])

            # Courier-wise stacked area chart
            st.markdown("### 🚚 Courier-wise Order Trend")
            stacked = df.groupby([df["GroupDate"], "Courier"]).size().unstack().fillna(0)
            st.area_chart(stacked)

            # Top products
            st.markdown("### 🥇 Top 5 Products")
            top_products = df["Product"].value_counts().head(5)
            st.dataframe(top_products)

        else:
            st.warning("⚠️ 'Order Date' column not found.")
