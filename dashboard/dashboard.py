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
    # Membaca file
    data = pd.read_csv(path, sep=None, engine='python')
    data.columns = data.columns.str.strip().str.lower()
    
    # Konversi tanggal dan bersihkan baris kosong
    if 'order_purchase_timestamp' in data.columns:
        data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'], errors='coerce')
        data = data.dropna(subset=['order_purchase_timestamp'])
    return data

# Jalankan Load Data
df = load_data(file_path) if os.path.exists(file_path) else None

if df is None:
    st.error("File tidak ditemukan!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Filter Dashboard")
    
    min_date = df['order_purchase_timestamp'].min().date()
    max_date = df['order_purchase_timestamp'].max().date()
    
    date_range = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    selected_states = st.multiselect("Pilih Negara Bagian", 
                                     options=sorted(df['customer_state'].unique()), 
                                     default=df['customer_state'].unique())

    selected_categories = st.multiselect("Pilih Kategori", 
                                         options=sorted(df['product_category_name_english'].dropna().unique()), 
                                         default=df['product_category_name_english'].dropna().unique()[:10])

# --- LOGIKA FILTERING (METODE MASKING TUNGGAL) ---
if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = (date_range[0] if isinstance(date_range, list) else date_range)

# Samakan format untuk perbandingan
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date) + pd.Timedelta(hours=23, minutes=59, seconds=59)

# KUNCI: Kita buat saringan (mask) langsung dari df utama
mask = (
    (df["order_purchase_timestamp"] >= start_dt) & 
    (df["order_purchase_timestamp"] <= end_dt) &
    (df["customer_state"].isin(selected_states)) &
    (df["product_category_name_english"].isin(selected_categories))
)

# Buat dataframe baru untuk visualisasi
main_df = df.loc[mask].copy()

# --- TAMPILAN UTAMA ---
st.title('Analisis Performa E-Commerce Olist 📊')

# Menampilkan statistik baris data agar Anda yakin data tidak hilang
st.write(f"Total data di file: **{len(df)}** | Data setelah difilter: **{len(main_df)}**")

if not main_df.empty:
    # METRICS
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", value=main_df['order_id'].nunique())
    with col2:
        st.metric("Total Revenue", value=f"R$ {main_df['price'].sum():,.2f}")
    with col3:
        st.metric("Total Customers", value=main_df['customer_id'].nunique())

    st.divider()

    # CHARTS
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
    st.warning("Data kosong untuk filter yang dipilih.")

st.caption('Copyright (c) 2025 - Olist Analysis')