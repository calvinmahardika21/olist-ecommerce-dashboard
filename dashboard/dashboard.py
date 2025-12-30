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
    # 1️⃣ Coba baca pakai delimiter ;
    try:
        df = pd.read_csv(path, sep=";")
        if df.shape[1] == 1:  # gagal parsing
            df = pd.read_csv(path, sep=",")
    except Exception:
        df = pd.read_csv(path)

    # 2️⃣ Bersihkan nama kolom (anti GitHub / Linux / BOM)
    df.columns = (
        df.columns
        .astype(str)
        .str.replace('\ufeff', '', regex=False)
        .str.replace('\r', '', regex=False)
        .str.replace('\n', '', regex=False)
        .str.replace('\t', '', regex=False)
        .str.replace('"', '', regex=False)
        .str.strip()
        .str.lower()
    )

    # 3️⃣ Validasi kolom penting
    required_cols = [
        "order_id",
        "customer_id",
        "customer_state",
        "product_category_name_english",
        "price",
        "order_purchase_timestamp"
    ]

    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        st.error("❌ Struktur CSV tidak sesuai")
        st.write("Kolom yang tersedia:", df.columns.tolist())
        st.write("Kolom yang dibutuhkan:", required_cols)
        st.stop()

    # 4️⃣ Konversi tanggal (aman untuk DD/MM/YYYY HH:MM)
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
    selected_states = st.multiselect(
        "Pilih Negara Bagian",
        options=states,
        default=states
    )

    categories = sorted(
        df_all["product_category_name_english"].dropna().unique()
    )
    selected_categories = st.multiselect(
        "Pilih Kategori Produk",
        options=categories,
        default=categories[:10]
    )

# ======================
# FILTER DATA
# ======================
start_dt = pd.to_datetime(date_range[0])
end_dt = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)

main_df = df_all[
    (df_all["order_purchase_timestamp"] >= start_dt) &
    (df_all["order_purchase_timestamp"] < end_dt)
]

main_df = main_df[
    main_df["customer_state"].isin(selected_states)
]

main_df = main_df[
    main_df["product_category_name_english"].isin(selected_categories)
]

# ======================
# TAMPILAN UTAMA
# ======================
st.title("📊 Analisis Performa E-Commerce Olist")

st.info(
    f"Memuat **{len(main_df)}** baris data "
    f"dari total **{len(df_all)}** baris data."
)

if main_df.empty:
    st.warning("Data kosong. Silakan ubah filter.")
    st.stop()

# ======================
# METRICS
# ======================
c1, c2, c3 = st.columns(3)

c1.metric("Total Orders", main_df["order_id"].nunique())
c2.metric("Total Revenue", f"R$ {main_df['price'].sum():,.2f}")
c3.metric("Total Customers", main_df["customer_id"].nunique())

st.divider()

# ======================
# VISUALISASI
# ======================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Kategori Produk (Revenue)")
    cat_df = (
        main_df.groupby("product_category_name_english")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=cat_df,
        x="price",
        y="product_category_name_english",
        ax=ax
    )
    ax.set_xlabel("Total Revenue (BRL)")
    ax.set_ylabel("Kategori Produk")
    st.pyplot(fig)

with col2:
    st.subheader("Top 10 Negara Bagian (Jumlah Pesanan)")
    state_df = (
        main_df.groupby("customer_state")["order_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=state_df,
        x="order_id",
        y="customer_state",
        ax=ax
    )
    ax.set_xlabel("Jumlah Pesanan")
    ax.set_ylabel("Negara Bagian")
    st.pyplot(fig)

st.caption("© 2025 - Olist E-Commerce Dashboard")
