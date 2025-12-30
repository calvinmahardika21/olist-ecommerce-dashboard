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
    return data

if os.path.exists(file_path):
    df = load_data(file_path)
else:
    st.error("File tidak ditemukan!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
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
    selected_states = st.multiselect("Pilih Wilayah", options=all_states, default=all_states)

# --- LOGIKA FILTERING (CARA TERAMAN) ---
if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = (date_range[0] if isinstance(date_range, list) else date_range)

# KUNCI PERBAIKAN: Kita ubah pembandingnya menjadi format yang sama persis
# Kita buat filter menggunakan kolom datetime yang dipotong jamnya
main_df = df.copy()
# Kita pastikan filternya juga bertipe datetime
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date) + pd.Timedelta(hours=23, minutes=59, seconds=59)

main_df = main_df[
    (main_df["order_purchase_timestamp"] >= start_dt) & 
    (main_df["order_purchase_timestamp"] <= end_dt) &
    (main_df["customer_state"].isin(selected_states))
]

# --- TAMPILAN UTAMA ---
st.title('Analisis Performa E-Commerce Olist 📊')

# CEK JUMLAH DATA (Agar kamu yakin tidak ada yang hilang)
st.info(f"💡 Menampilkan **{len(main_df)}** baris data dari total **{len(df)}** baris.")

if not main_df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", value=main_df['order_id'].nunique())
    with col2:
        st.metric("Total Revenue", value=f"R$ {main_df['price'].sum():,.2f}")
    with col3:
        st.metric("Total Customers", value=main_df['customer_id'].nunique())
    
    st.divider()
    
    # Visualisasi Sederhana
    st.subheader("Orders by State")
    state_df = main_df.groupby("customer_state")['order_id'].nunique().sort_values(ascending=False).head(10).reset_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x="order_id", y="customer_state", data=state_df, palette="viridis", ax=ax)
    st.pyplot(fig)
else:
    st.warning("Data tidak ditemukan untuk filter ini.")

st.caption('Copyright (c) 2025')