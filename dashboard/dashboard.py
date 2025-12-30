import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# =============================
# KONFIGURASI HALAMAN
# =============================
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    layout="wide"
)

# =============================
# LOAD DATA
# =============================
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "main_data.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = df.columns.str.strip().str.lower()

    # pastikan timestamp datetime
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce"
    )

    df = df.dropna(subset=["order_purchase_timestamp"])
    return df.reset_index(drop=True)

if not os.path.exists(file_path):
    st.error("❌ File main_data.csv tidak ditemukan")
    st.stop()

df_all = load_data(file_path)

# =============================
# SIDEBAR FILTER
# =============================
with st.sidebar:
    st.header("Filter Data")

    min_date = df_all["order_purchase_timestamp"].min().date()
    max_date = df_all["order_purchase_timestamp"].max().date()

    date_range = st.date_input(
        "Rentang Waktu",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    selected_states = st.multiselect(
        "Customer State",
        options=sorted(df_all["customer_state"].dropna().unique()),
        default=sorted(df_all["customer_state"].dropna().unique())
    )

    selected_categories = st.multiselect(
        "Product Category",
        options=sorted(df_all["product_category_name_english"].dropna().unique()),
        default=sorted(df_all["product_category_name_english"].dropna().unique())[:10]
    )

# =============================
# FILTERING DATA (AMAN)
# =============================
start_dt = pd.to_datetime(date_range[0])
end_dt = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)

main_df = df_all[
    (df_all["order_purchase_timestamp"] >= start_dt) &
    (df_all["order_purchase_timestamp"] < end_dt)
].copy()

main_df = main_df[main_df["customer_state"].isin(selected_states)]
main_df = main_df[main]()
