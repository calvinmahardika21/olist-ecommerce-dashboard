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
main_df = main_df[main_df["product_category_name_english"].isin(selected_categories)]

# =============================
# TAMPILAN UTAMA
# =============================
st.title("Analisis Performa E-Commerce Olist 📊")
st.caption(f"Menampilkan **{len(main_df)}** baris dari total **{len(df_all)}** data")

if main_df.empty:
    st.warning("Data kosong, silakan ubah filter.")
    st.stop()

# =============================
# METRICS (ANTI ERROR)
# =============================
col1, col2, col3 = st.columns(3)

# Total Orders (DEFENSIVE)
if "order_id" in main_df.columns:
    total_orders = main_df["order_id"].nunique()
else:
    total_orders = len(main_df)

with col1:
    st.metric("Total Orders", total_orders)

with col2:
    st.metric("Total Revenue", f"R$ {main_df['price'].sum():,.2f}")

with col3:
    st.metric("Total Customers", main_df["customer_id"].nunique())

st.divider()

# =============================
# VISUALISASI
# =============================
c1, c2 = st.columns(2)

with c1:
    st.subheader("Top 10 Categories by Revenue")
    top_cat = (
        main_df.groupby("product_category_name_english")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=top_cat,
        x="price",
        y="product_category_name_english",
        ax=ax
    )
    st.pyplot(fig)

with c2:
    st.subheader("Top 10 States by Orders")
    state_orders = (
        main_df.groupby("customer_state")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="total_orders")
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=state_orders,
        x="total_orders",
        y="customer_state",
        ax=ax
    )
    st.pyplot(fig)

st.caption("© 2025 — Olist E-Commerce Analysis Dashboard")
