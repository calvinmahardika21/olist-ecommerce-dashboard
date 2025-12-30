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
    data = pd.read_csv(path)
    data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])
    return data

# Cek apakah file ada
if os.path.exists(file_path):
    df = load_data(file_path)
else:
    st.error(f"File {file_path} tidak ditemukan! Pastikan main_data.csv ada di folder dashboard.")
    st.stop()

# --- SIDEBAR (FITUR INTERAKTIF) ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Konfigurasi Filter")
    
    # 1. Filter Rentang Waktu
    min_date = df['order_purchase_timestamp'].min()
    max_date = df['order_purchase_timestamp'].max()
    
    try:
        # User input rentang waktu
        date_range = st.date_input(
            label='Rentang Waktu Analisis',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
        
        # Penanganan jika user baru memilih satu tanggal
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range[0]
            
    except Exception:
        st.error("Pilih rentang tanggal yang valid.")
        st.stop()

    # 2. Filter Negara Bagian (State)
    st.write("### Wilayah Pelanggan")
    all_states = sorted(df['customer_state'].unique())
    selected_states = st.multiselect(
        label="Pilih Negara Bagian (State)",
        options=all_states,
        default=all_states
    )

    # 3. Filter Kategori Produk
    st.write("### Kategori Produk")
    all_categories = sorted(df['product_category_name_english'].dropna().unique().astype(str))
    selected_categories = st.multiselect(
        label="Pilih Kategori",
        options=all_categories,
        default=all_categories[:10] # Default pilih 10 kategori pertama agar grafik terlihat bagus
    )

# --- LOGIKA FILTERING ---
main_df = df[
    (df["order_purchase_timestamp"].dt.date >= start_date) & 
    (df["order_purchase_timestamp"].dt.date <= end_date) &
    (df["product_category_name_english"].isin(selected_categories)) &
    (df["customer_state"].isin(selected_states))
]

# --- TAMPILAN UTAMA ---
st.title('Analisis Performa E-Commerce Olist 📊')
st.markdown(f"Menampilkan data untuk **{len(selected_categories)}** kategori di **{len(selected_states)}** wilayah.")

# --- 1. METRICS ---
col_metric1, col_metric2, col_metric3 = st.columns(3)
with col_metric1:
    st.metric("Total Orders", value=main_df.order_id.nunique())
with col_metric2:
    total_rev = main_df.price.sum()
    st.metric("Total Revenue", value=f"R$ {total_rev:,.2f}")
with col_metric3:
    st.metric("Total Customers", value=main_df.customer_id.nunique())

st.divider()

# --- 2. GEOGRAPHICAL & PRODUCT ANALYSIS ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Top Categories by Revenue")
    if not main_df.empty:
        # Menyiapkan data 10 teratas
        top_10_df = main_df.groupby("product_category_name_english").price.sum().sort_values(ascending=False).head(10).reset_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Logika Warna: Biru untuk ranking 1, Abu-abu untuk sisanya
        colors = ["#72BCD4"] + ["#D3D3D3"] * (len(top_10_df) - 1)
        
        sns.barplot(
            x="price", 
            y="product_category_name_english", 
            data=top_10_df, 
            palette=colors, 
            ax=ax
        )
        
        ax.set_xlabel("Total Revenue (BRL)")
        ax.set_ylabel(None)
        ax.set_title("10 Kategori Produk dengan Pendapatan Tertinggi", fontsize=12)
        st.pyplot(fig)
    else:
        st.warning("Data tidak tersedia.")

with col_chart2:
    st.subheader("Orders by State")
    if not main_df.empty:
        state_df = main_df.groupby("customer_state").order_id.nunique().sort_values(ascending=False).head(10).reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.barplot(x="order_id", y="customer_state", data=state_df, palette="rocket", ax=ax)
        
        ax.set_xlabel("Number of Orders")
        ax.set_ylabel("State")
        ax.set_title("10 Negara Bagian dengan Pesanan Terbanyak", fontsize=12)
        st.pyplot(fig)
    else:
        st.warning("Data tidak tersedia.")

# --- 3. RFM ANALYSIS ---
st.divider()
st.subheader("Best Customer Based on RFM Parameters")

if not main_df.empty:
    recent_date = main_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = main_df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": lambda x: (recent_date - x.max()).days,
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]

    def shorten_id(df):
        return df['customer_id'].str[:10] + "..."

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("#### By Recency (Days)")
        top_rec = rfm_df.sort_values("recency").head(5).copy()
        top_rec['id_short'] = shorten_id(top_rec)
        fig, ax = plt.subplots()
        sns.barplot(y="recency", x="id_short", data=top_rec, palette="Reds", ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with col2:
        st.write("#### By Frequency")
        top_freq = rfm_df.sort_values("frequency", ascending=False).head(5).copy()
        top_freq['id_short'] = shorten_id(top_freq)
        fig, ax = plt.subplots()
        sns.barplot(y="frequency", x="id_short", data=top_freq, palette="Greens", ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with col3:
        st.write("#### By Monetary")
        top_mon = rfm_df.sort_values("monetary", ascending=False).head(5).copy()
        top_mon['id_short'] = shorten_id(top_mon)
        fig, ax = plt.subplots()
        sns.barplot(y="monetary", x="id_short", data=top_mon, palette="Blues", ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
else:
    st.info("Gunakan filter di sidebar untuk melihat data.")

st.caption('Copyright (c) 2025 - Olist E-Commerce Analysis')