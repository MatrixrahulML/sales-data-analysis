# 📊 Sales Data Analysis Dashboard

An interactive Streamlit dashboard analyzing 8,399 real Superstore orders
(2009–2012): sales/profit trends, regional & category breakdowns, customer
segments, and shipping operations — with live filters on date range, region,
category, and customer segment.

## What's inside

- `prepare_data.py` — cleans the raw dataset (dates, missing margin values),
  engineers features (month/quarter/weekday, shipping days, profit margin,
  profitability flag)
- `app.py` — the Streamlit dashboard with five pages:
  - **Overview** — KPIs, monthly sales/profit trend, category & weekday breakdowns, top 10 products
  - **Regions & Categories** — regional sales map/pie, category→sub-category treemap, profit margin by category, top provinces
  - **Customers** — segment breakdown, top 15 customers, order priority distribution
  - **Operations** — shipping time distribution, discount vs. profit margin scatter, profitability by ship mode
  - **Raw Data** — searchable, filterable table with CSV export
- `superstore.csv` — original raw dataset
- `sales_clean.csv` — cleaned/engineered dataset the app reads from

**Dataset stats:** $14.9M total sales, $1.5M total profit, 2009–2012, 8 regions, 3 product categories, 4 customer segments.

## Run locally

```bash
pip install -r requirements.txt
python prepare_data.py     # optional — sales_clean.csv is already included
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to GitHub (standalone repo, or as a subfolder in
   `my-data-science-projects` — see the shared deployment guide for both options)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Pick the repo, set main file to `app.py` (or `sales-data-analysis/app.py`
   if nested in the portfolio repo)
4. Deploy — `sales_clean.csv` is already committed, so no data prep step
   runs on the cloud

See `DEPLOYMENT_GUIDE.md` for the full click-by-click process (same steps
used for the Titanic project).
