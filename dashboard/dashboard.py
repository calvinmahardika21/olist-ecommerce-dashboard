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
    # Membersihkan nama kolom (huruf kecil & tanpa spasi)
    data.columns = data.columns.str.strip().str.lower()
    # Konversi waktu
    if 'order_purchase_timestamp' in data.columns:
        data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])
    return data

# Jalankan Load Data
if os.path.exists(file_path):
    df = load_data(file_path)
else:
    st.error(f"File tidak ditemukan!")
    st.stop()

# --- SIDEBAR (FITUR INTERAKTIF) ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Konfigurasi Filter")
    
    # Filter Rentang Waktu
    min_date = df['order_purchase_timestamp'].min().date()
    max_date = df['order_purchase_timestamp'].max().date()
    
    date_range = st.date_input(
        label='Rentang Waktu Analisis',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter Negara Bagian (State)
    all_states = sorted(df['customer_state'].unique())
    selected_states = st.multiselect("Pilih Negara Bagian", options=all_states, default=all_states)

    # Filter Kategori Produk
    all_categories = sorted(df['product_category_name_english'].dropna().unique())
    selected_categories = st.multiselect("Pilih Kategori", options=all_categories, default=all_categories[:10])

# --- LOGIKA FILTERING ---
# Pastikan filter tanggal aman
if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

main_df = df[
    (df["order_purchase_timestamp"].dt.date >= start_date) & 
    (df["order_purchase_timestamp"].dt.date <= end_date) &
    (df["product_category_name_english"].isin(selected_categories)) &
    (df["customer_state"].isin(selected_states))
]

# --- TAMPILAN UTAMA ---
st.title('Analisis Performa E-Commerce Olist 📊')

# --- 1. METRICS (Gunakan Kurung Siku Agar Aman) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Orders", value=main_df['order_id'].nunique())
with col2:
    total_rev = main_df['price'].sum()
    st.metric("Total Revenue", value=f"R$ {total_rev:,.2f}")
with col3:
    st.metric("Total Customers", value=main_df['customer_id'].nunique())

st.divider()

# --- 2. VISUALISASI ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Top Categories by Revenue")
    if not main_df.empty:
        top_df = main_df.groupby("product_category_name_english")['price'].sum().sort_values(ascending=False).head(10).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="price", y="product_category_name_english", data=top_df, palette="viridis", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("Data tidak tersedia untuk filter ini.")

with col_chart2:
    st.subheader("Orders by State")
    if not main_df.empty:
        state_df = main_df.groupby("customer_state")['order_id'].nunique().sort_values(ascending=False).head(10).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="order_id", y="customer_state", data=state_df, palette="magma", ax=ax)
        st.pyplot(fig)

st.caption('Copyright (c) 2025 - Olist E-Commerce Analysis')