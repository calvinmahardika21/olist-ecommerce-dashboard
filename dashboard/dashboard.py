import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Olist E-Commerce Dashboard")

# --- LOAD DATA ---
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "main_data.csv")

@st.cache_data
def load_data(path):
    # Membaca file dengan deteksi separator otomatis
    data = pd.read_csv(path, sep=None, engine='python')
    data.columns = data.columns.str.strip().str.lower()
    
    # Konversi kolom waktu ke datetime murni
    if 'order_purchase_timestamp' in data.columns:
        data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'], errors='coerce')
        # Hapus baris yang benar-benar tidak punya tanggal agar tidak error saat difilter
        data = data.dropna(subset=['order_purchase_timestamp'])
    return data

if os.path.exists(file_path):
    df = load_data(file_path)
else:
    st.error("File tidak ditemukan!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Filter Data")
    
    # Ambil nilai min dan max tanggal
    min_date = df['order_purchase_timestamp'].min().date()
    max_date = df['order_purchase_timestamp'].max().date()
    
    date_range = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    all_states = sorted(df['customer_state'].unique())
    selected_states = st.multiselect("Pilih Negara Bagian", options=all_states, default=all_states)

    all_categories = sorted(df['product_category_name_english'].dropna().unique())
    selected_categories = st.multiselect("Pilih Kategori", options=all_categories, default=all_categories[:10])

# --- LOGIKA FILTERING (DIPERBAIKI) ---
if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = (date_range[0] if isinstance(date_range, list) else date_range)

# Konversi filter user ke datetime
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date) + pd.Timedelta(hours=23, minutes=59, seconds=59)

# Lakukan filter sekaligus pada dataframe asli (df)
main_df = df[
    (df["order_purchase_timestamp"] >= start_dt) & 
    (df["order_purchase_timestamp"] <= end_dt) &
    (df["customer_state"].isin(selected_states)) &
    (df["product_category_name_english"].isin(selected_categories))
].copy()

# --- TAMPILAN UTAMA ---
st.title('Analisis Performa E-Commerce Olist 📊')
st.info(f"💡 Menampilkan **{len(main_df)}** baris data.")

if not main_df.empty:
    # 1. METRICS
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total Orders", value=main_df['order_id'].nunique())
    with col_m2:
        st.metric("Total Revenue", value=f"R$ {main_df['price'].sum():,.2f}")
    with col_m3:
        st.metric("Total Customers", value=main_df['customer_id'].nunique())

    st.divider()

    # 2. CHARTS
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top Categories by Revenue")
        top_df = main_df.groupby("product_category_name_english")['price'].sum().sort_values(ascending=False).head(10).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="price", y="product_category_name_english", data=top_df, palette="viridis", ax=ax)
        st.pyplot(fig)

    with c2:
        st.subheader("Orders by State")
        state_df = main_df.groupby("customer_state")['order_id'].nunique().sort_values(ascending=False).head(10).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="order_id", y="customer_state", data=state_df, palette="magma", ax=ax)
        st.pyplot(fig)

    # 3. RFM ANALYSIS
    st.divider()
    st.subheader("Best Customer Based on RFM Parameters")
    
    recent_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = main_df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": lambda x: (recent_date - x.max()).days,
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.write("#### By Recency (Days)")
        fig, ax = plt.subplots()
        sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values("recency").head(5), palette="Reds", ax=ax)
        ax.set_xticklabels([]) # Sembunyikan ID karena terlalu panjang
        st.pyplot(fig)
    with col_r2:
        st.write("#### By Frequency")
        fig, ax = plt.subplots()
        sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values("frequency", ascending=False).head(5), palette="Greens", ax=ax)
        ax.set_xticklabels([])
        st.pyplot(fig)
    with col_r3:
        st.write("#### By Monetary")
        fig, ax = plt.subplots()
        sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values("monetary", ascending=False).head(5), palette="Blues", ax=ax)
        ax.set_xticklabels([])
        st.pyplot(fig)

else:
    st.warning("Data tidak ditemukan. Silakan atur ulang filter.")

st.caption('Copyright (c) 2025 - Olist Analysis')