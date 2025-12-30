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
    # Membaca data dengan deteksi otomatis
    data = pd.read_csv(path, sep=None, engine='python')
    data.columns = data.columns.str.strip().str.lower()
    
    # Konversi tanggal dan pastikan index bersih
    if 'order_purchase_timestamp' in data.columns:
        data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'], errors='coerce')
        data = data.dropna(subset=['order_purchase_timestamp'])
    
    return data.reset_index(drop=True)

if os.path.exists(file_path):
    # Kita gunakan df_all sebagai sumber data master yang tidak berubah
    df_all = load_data(file_path)
else:
    st.error("File main_data.csv tidak ditemukan!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Filter Data")
    
    # Ambil batas tanggal
    min_date = df_all['order_purchase_timestamp'].min().date()
    max_date = df_all['order_purchase_timestamp'].max().date()
    
    date_range = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Menyiapkan list untuk filter
    all_states = sorted(df_all['customer_state'].unique())
    selected_states = st.multiselect("Pilih Negara Bagian", options=all_states, default=all_states)

    all_cats = sorted(df_all['product_category_name_english'].dropna().unique())
    selected_categories = st.multiselect("Pilih Kategori", options=all_cats, default=all_cats[:10])

# --- LOGIKA FILTERING (METODE QUERY - ANTI ERROR) ---
if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = (date_range[0] if isinstance(date_range, list) else date_range)

# Ubah ke format datetime untuk filter
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date) + pd.Timedelta(hours=23, minutes=59, seconds=59)

# KUNCI: Gunakan .query() atau filter bertahap pada salinan lokal
# Cara ini menjamin tidak ada 'length mismatch'
main_df = df_all[
    (df_all["order_purchase_timestamp"] >= start_dt) & 
    (df_all["order_purchase_timestamp"] <= end_dt)
].copy()

main_df = main_df[main_df["customer_state"].isin(selected_states)]
main_df = main_df[main_df["product_category_name_english"].isin(selected_categories)]

# --- TAMPILAN UTAMA ---
st.title('Analisis Performa E-Commerce Olist 📊')

# Menampilkan info baris untuk membuktikan data tidak hilang
st.info(f"💡 Memuat **{len(main_df)}** baris data dari total **{len(df_all)}** baris master.")

if not main_df.empty:
    # 1. METRICS
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Orders", value=main_df['order_id'].nunique())
    with m2:
        st.metric("Total Revenue", value=f"R$ {main_df['price'].sum():,.2f}")
    with m3:
        st.metric("Total Customers", value=main_df['customer_id'].nunique())

    st.divider()

    # 2. VISUALISASI
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top Categories")
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
else:
    st.warning("Data tidak ditemukan. Silakan sesuaikan filter Anda.")

st.caption('Copyright (c) 2025 - Olist Analysis Dashboard')