import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# ======================
# KONFIGURASI HALAMAN
# ======================
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    layout="wide"
)

# ======================
# LOAD DATA (SUPER ROBUST)
# ======================
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "main_data.csv")

@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path, sep=";")
        if df.shape[1] == 1:  
            df = pd.read_csv(path, sep=",")
    except Exception:
        df = pd.read_csv(path)

    df.columns = (
        df.columns
        .astype(str)
        .str.replace('\ufeff', '', regex=False)
        .str.strip()
        .str.lower()
    )

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce",
        dayfirst=True
    )
    df = df.dropna(subset=["order_purchase_timestamp"])
    return df.reset_index(drop=True)

if not os.path.exists(file_path):
    st.error("❌ File main_data.csv tidak ditemukan.")
    st.stop()

df_all = load_data(file_path)

# ======================
# SIDEBAR FILTER
# ======================
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

    states = sorted(df_all["customer_state"].dropna().unique())
    selected_states = st.multiselect("Pilih Negara Bagian", options=states, default=states)

    categories = sorted(df_all["product_category_name_english"].dropna().unique())
    selected_categories = st.multiselect("Pilih Kategori Produk", options=categories, default=categories[:10])

# ======================
# FILTER LOGIC
# ======================
if len(date_range) == 2:
    start_dt = pd.to_datetime(date_range[0])
    end_dt = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
else:
    st.stop()

main_df = df_all[
    (df_all["order_purchase_timestamp"] >= start_dt) & 
    (df_all["order_purchase_timestamp"] < end_dt) &
    (df_all["customer_state"].isin(selected_states)) &
    (df_all["product_category_name_english"].isin(selected_categories))
].copy()

# ======================
# TAMPILAN UTAMA
# ======================
st.title("📊 Analisis Performa E-Commerce Olist")

n_categories = main_df["product_category_name_english"].nunique()
n_states = main_df["customer_state"].nunique()
st.info(f"Menampilkan data untuk **{n_categories}** kategori di **{n_states}** wilayah.")

if main_df.empty:
    st.warning("Data kosong. Silakan ubah filter.")
    st.stop()

# METRICS
c1, c2, c3 = st.columns(3)
c1.metric("Total Orders", main_df["order_id"].nunique())
c2.metric("Total Revenue", f"R$ {main_df['price'].sum():,.2f}")
c3.metric("Total Customers", main_df["customer_id"].nunique())

st.divider()

# VISUALISASI UTAMA
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Categories by Revenue")
    cat_df = main_df.groupby("product_category_name_english")["price"].sum().sort_values(ascending=False).head(10).reset_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=cat_df, x="price", y="product_category_name_english", palette="viridis", ax=ax)
    st.pyplot(fig)

with col2:
    st.subheader("Orders by State")
    state_df = main_df.groupby("customer_state")["order_id"].nunique().sort_values(ascending=False).head(10).reset_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=state_df, x="order_id", y="customer_state", palette="rocket", ax=ax)
    st.pyplot(fig)

st.divider()

# ======================
# ANALISIS RFM
# ======================
st.subheader("Best Customer Based on RFM Parameters")

# Tanggal referensi untuk Recency
latest_date = df_all["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

rfm_df = main_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": lambda x: (latest_date - x.max()).days, # Recency
    "order_id": "nunique", # Frequency
    "price": "sum" # Monetary
})
rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]

col_r, col_f, col_m = st.columns(3)

with col_r:
    st.write("#### By Recency (Days)")
    top_r = rfm_df.sort_values(by="recency", ascending=True).head(5)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y="recency", x="customer_id", data=top_r, palette="Reds", ax=ax)
    ax.set_xticklabels([f"{x[:5]}..." for x in top_r["customer_id"]], rotation=45)
    st.pyplot(fig)

with col_f:
    st.write("#### By Frequency")
    top_f = rfm_df.sort_values(by="frequency", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y="frequency", x="customer_id", data=top_f, palette="Greens", ax=ax)
    ax.set_xticklabels([f"{x[:5]}..." for x in top_f["customer_id"]], rotation=45)
    st.pyplot(fig)

with col_m:
    st.write("#### By Monetary")
    top_m = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y="monetary", x="customer_id", data=top_m, palette="Blues", ax=ax)
    ax.set_xticklabels([f"{x[:5]}..." for x in top_m["customer_id"]], rotation=45)
    st.pyplot(fig)

st.caption("© 2025 - Olist E-Commerce Dashboard")