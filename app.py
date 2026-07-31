import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Sales Data Analysis", page_icon="📊", layout="wide")


# Load data

@st.cache_data
def load_data():
    df = pd.read_csv("sales_clean.csv", parse_dates=["Order Date", "Ship Date"])
    return df

df = load_data()


# Sidebar — filters

st.sidebar.title("📊 Sales Data Analysis")
st.sidebar.caption("Superstore dataset · 8,399 orders · 2009–2012")
st.sidebar.markdown("---")
st.sidebar.header("Filters")

min_date, max_date = df["Order Date"].min(), df["Order Date"].max()
date_range = st.sidebar.date_input(
    "Order date range", value=(min_date, max_date),
    min_value=min_date, max_value=max_date
)

regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()), default=[])
categories = st.sidebar.multiselect("Product Category", sorted(df["Product Category"].unique()), default=[])
segments = st.sidebar.multiselect("Customer Segment", sorted(df["Customer Segment"].unique()), default=[])

# Apply filters
fdf = df.copy()
if len(date_range) == 2:
    fdf = fdf[(fdf["Order Date"] >= pd.Timestamp(date_range[0])) &
              (fdf["Order Date"] <= pd.Timestamp(date_range[1]))]
if regions:
    fdf = fdf[fdf["Region"].isin(regions)]
if categories:
    fdf = fdf[fdf["Product Category"].isin(categories)]
if segments:
    fdf = fdf[fdf["Customer Segment"].isin(segments)]

st.sidebar.markdown("---")
st.sidebar.caption(f"**{len(fdf):,}** orders match current filters")

if len(fdf) == 0:
    st.warning("No orders match the selected filters. Adjust filters in the sidebar.")
    st.stop()


# Sidebar — navigation

page = st.sidebar.radio("Navigate", ["📈 Overview", "🗺️ Regions & Categories",
                                       "👥 Customers", "🚚 Operations", "🔍 Raw Data"])


# PAGE: Overview

if page == "📈 Overview":
    st.title("Sales Overview")

    total_sales = fdf["Sales"].sum()
    total_profit = fdf["Profit"].sum()
    total_orders = fdf["Order ID"].nunique()
    avg_order_value = fdf.groupby("Order ID")["Sales"].sum().mean()
    profit_margin = total_profit / total_sales if total_sales else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Sales", f"${total_sales:,.0f}")
    c2.metric("Total Profit", f"${total_profit:,.0f}")
    c3.metric("Orders", f"{total_orders:,}")
    c4.metric("Avg Order Value", f"${avg_order_value:,.0f}")
    c5.metric("Profit Margin", f"{profit_margin:.1%}")

    st.markdown("---")

    monthly = fdf.groupby(fdf["Order Date"].dt.to_period("M")).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum")
    ).reset_index()
    monthly["Order Date"] = monthly["Order Date"].dt.to_timestamp()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["Order Date"], y=monthly["Sales"],
                              name="Sales", mode="lines+markers", line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=monthly["Order Date"], y=monthly["Profit"],
                              name="Profit", mode="lines+markers", line=dict(color="#2E7D32")))
    fig.update_layout(title="Monthly Sales & Profit Trend", height=420,
                       xaxis_title="Month", yaxis_title="USD ($)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        cat_sales = fdf.groupby("Product Category")["Sales"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(cat_sales, x="Product Category", y="Sales", title="Sales by Category",
                     color="Product Category")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        wd_sales = fdf.groupby("Weekday")["Sales"].sum().reindex(weekday_order).reset_index()
        fig = px.bar(wd_sales, x="Weekday", y="Sales", title="Sales by Day of Week")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Products by Sales")
    top_products = fdf.groupby("Product Name").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")
    ).sort_values("Sales", ascending=False).head(10).reset_index()
    fig = px.bar(top_products, x="Sales", y="Product Name", orientation="h",
                 title="Top 10 Products", color="Profit", color_continuous_scale="RdYlGn")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=450)
    st.plotly_chart(fig, use_container_width=True)


# PAGE: Regions & Categories

elif page == "🗺️ Regions & Categories":
    st.title("Regional & Category Breakdown")

    c1, c2 = st.columns(2)
    with c1:
        region_sales = fdf.groupby("Region").agg(
            Sales=("Sales", "sum"), Profit=("Profit", "sum")
        ).sort_values("Sales", ascending=False).reset_index()
        fig = px.bar(region_sales, x="Region", y="Sales", title="Sales by Region", color="Profit",
                     color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(region_sales, names="Region", values="Sales", title="Sales Share by Region", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Category × Sub-Category")
    sub_sales = fdf.groupby(["Product Category", "Product Sub-Category"])["Sales"].sum().reset_index()
    fig = px.treemap(sub_sales, path=["Product Category", "Product Sub-Category"], values="Sales",
                      title="Sales Treemap: Category → Sub-Category", color="Sales",
                      color_continuous_scale="Blues")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Profit Margin by Category")
    margin_df = fdf.groupby("Product Category").apply(
        lambda x: x["Profit"].sum() / x["Sales"].sum(), include_groups=False
    ).reset_index()
    margin_df.columns = ["Product Category", "ProfitMargin"]
    fig = px.bar(margin_df, x="Product Category", y="ProfitMargin", title="Profit Margin by Category",
                 color="ProfitMargin", color_continuous_scale="RdYlGn")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sales by Province (Top 15)")
    prov_sales = fdf.groupby("Province")["Sales"].sum().sort_values(ascending=False).head(15).reset_index()
    fig = px.bar(prov_sales, x="Sales", y="Province", orientation="h", title="Top 15 Provinces by Sales")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)


# PAGE: Customers

elif page == "👥 Customers":
    st.title("Customer Analysis")

    c1, c2 = st.columns(2)
    with c1:
        seg_sales = fdf.groupby("Customer Segment")["Sales"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(seg_sales, x="Customer Segment", y="Sales", title="Sales by Customer Segment",
                     color="Customer Segment")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        seg_orders = fdf.groupby("Customer Segment")["Order ID"].nunique().reset_index()
        seg_orders.columns = ["Customer Segment", "Orders"]
        fig = px.pie(seg_orders, names="Customer Segment", values="Orders", title="Order Share by Segment", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 15 Customers by Sales")
    top_customers = fdf.groupby("Customer Name").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")
    ).sort_values("Sales", ascending=False).head(15).reset_index()
    fig = px.bar(top_customers, x="Sales", y="Customer Name", orientation="h",
                 title="Top 15 Customers", color="Profit", color_continuous_scale="RdYlGn")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Order Priority Distribution")
    priority_counts = fdf["Order Priority"].value_counts().reset_index()
    priority_counts.columns = ["Order Priority", "Count"]
    fig = px.bar(priority_counts, x="Order Priority", y="Count", title="Orders by Priority Level",
                 color="Order Priority")
    st.plotly_chart(fig, use_container_width=True)


# PAGE: Operations

elif page == "🚚 Operations":
    st.title("Shipping & Operations")

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Shipping Days", f"{fdf['ShippingDays'].mean():.1f}")
    c2.metric("Avg Discount", f"{fdf['Discount'].mean():.1%}")
    c3.metric("Unprofitable Orders", f"{(1 - fdf['IsProfitable'].mean()):.1%}")

    c1, c2 = st.columns(2)
    with c1:
        ship_sales = fdf.groupby("Ship Mode")["Sales"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(ship_sales, x="Ship Mode", y="Sales", title="Sales by Ship Mode", color="Ship Mode")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(fdf, x="ShippingDays", nbins=20, title="Shipping Time Distribution (days)")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Discount vs Profit Margin")
    sample = fdf.sample(min(2000, len(fdf)), random_state=42)
    fig = px.scatter(sample, x="Discount", y="ProfitMargin", color="Product Category",
                      title="Does higher discount hurt margin?", opacity=0.6,
                      labels={"ProfitMargin": "Profit Margin"})
    fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Profitability by Ship Mode")
    ship_profit = fdf.groupby("Ship Mode").apply(
        lambda x: x["Profit"].sum() / x["Sales"].sum(), include_groups=False
    ).reset_index()
    ship_profit.columns = ["Ship Mode", "ProfitMargin"]
    fig = px.bar(ship_profit, x="Ship Mode", y="ProfitMargin", title="Profit Margin by Ship Mode",
                 color="ProfitMargin", color_continuous_scale="RdYlGn")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)


# PAGE: Raw Data

elif page == "🔍 Raw Data":
    st.title("Raw Data Explorer")
    st.markdown(f"Showing **{len(fdf):,}** rows matching current filters.")

    search = st.text_input("Search product or customer name")
    view = fdf.copy()
    if search:
        mask = (view["Product Name"].str.contains(search, case=False, na=False) |
                view["Customer Name"].str.contains(search, case=False, na=False))
        view = view[mask]

    display_cols = ["Order Date", "Customer Name", "Product Name", "Product Category",
                     "Region", "Province", "Sales", "Profit", "Discount", "Order Priority"]
    st.dataframe(view[display_cols].sort_values("Order Date", ascending=False),
                 use_container_width=True, height=450)

    csv = view[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_sales.csv", "text/csv")

st.markdown("---")
st.caption("Built By MatrixRahul with Streamlit · Plotly · Superstore sales dataset (2009–2012)")
