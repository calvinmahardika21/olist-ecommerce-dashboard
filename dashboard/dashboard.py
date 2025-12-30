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
    # Menggunakan engine python agar otomatis deteksi separator
    data = pd.read_csv(path, sep=None, engine='python')
    data.columns = data.columns.str.strip().str.lower()
    
    # Konversi tanggal dengan sangat hati-hati
    if 'order_purchase_timestamp' in data.columns:
        data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'], errors='coerce')
        # Kita hanya buang baris yang tanggalnya benar-benar kosong/corrupt
        data = data.dropna(subset=['order_purchase_timestamp'])
    
    return data

# Jalankan Load Data
if os.path.exists(file_path):
    df = load_data(file_path)
else:
    st.error("File main_data.csv tidak ditemukan!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Filter Dashboard")
    
    # Ambil batas tanggal dari data asli
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

# --- LOGIKA FILTERING (Satu Langkah Saja) ---
# Memastikan rentang tanggal aman
if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = (date_range[0] if isinstance(date_range, list) else date_range)

# Konversi filter ke datetime
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date) + pd.Timedelta(hours=23, minutes=59, seconds=59)

# KUNCI PERBAIKAN: Gunakan .loc dengan mask pada dataframe asli 'df'
# Ini menjamin perbandingan panjang data selalu sama (match)
mask = (
    (df["order_purchase_timestamp"] >= start_dt) & 
    (df["order_purchase_timestamp"] <= end_dt) &
    (df["customer_state"].isin(selected_states)) &
    (df["product_category_name_english"].isin(selected_categories))
)

main_df = df.loc[mask].copy()

# --- TAMPILAN UTAMA ---
st.title('Analisis Performa E-Commerce Olist 📊')

# Menampilkan indikator transparansi data
st.info(f"💡 Menampilkan **{len(main_df)}** baris data dari total **{len(df)}** baris di database.")

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
        fig, ax = plt.subplots()
        sns.barplot(x="price", y="product_category_name_english", data=top_df, palette="viridis", ax=ax)
        st.pyplot(fig)

    with c2:
        st.subheader("Orders by State")
        state_df = main_df.groupby("customer_state")['order_id'].nunique().sort_values(ascending=False).head(10).reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x="order_id", y="customer_state", data=state_df, palette="magma", ax=ax)
        st.pyplot(fig)
else:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter Anda.")

st.caption('Copyright (c) 2025 - Olist Analysis Dashboard')