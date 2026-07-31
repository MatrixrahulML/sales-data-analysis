"""
Clean and prepare the Superstore sales dataset for the Streamlit dashboard.
Run once before starting the app:
    python prepare_data.py
"""
import pandas as pd

df = pd.read_csv("superstore.csv", encoding="latin1")

# ---------------------------------------------------------------
# Clean & type columns
# ---------------------------------------------------------------
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

df["Product Base Margin"] = df["Product Base Margin"].fillna(
    df.groupby("Product Category")["Product Base Margin"].transform("median")
)

# ---------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------
df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
df["MonthName"] = df["Order Date"].dt.strftime("%b")
df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
df["Weekday"] = df["Order Date"].dt.day_name()

df["ShippingDays"] = (df["Ship Date"] - df["Order Date"]).dt.days
df["ProfitMargin"] = df["Profit"] / df["Sales"]
df["IsProfitable"] = (df["Profit"] > 0).astype(int)

df = df.sort_values("Order Date").reset_index(drop=True)

df.to_csv("sales_clean.csv", index=False)

print(f"Cleaned dataset: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Date range: {df['Order Date'].min().date()} to {df['Order Date'].max().date()}")
print(f"Total sales: ${df['Sales'].sum():,.0f}")
print(f"Total profit: ${df['Profit'].sum():,.0f}")
print("Saved sales_clean.csv")
