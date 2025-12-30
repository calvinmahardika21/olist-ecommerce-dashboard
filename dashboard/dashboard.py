import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    layout="wide",
    page_title="Olist E-Commerce Dashboard"
)

# --- LOAD DATA ---
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "main_data.csv")

@st.cache_data
def load_data(path):
    data = pd.read_csv(path, sep=None, engine="python")
    data.columns = data.columns.str.strip().str.lower()

    if "order_purchase_timestamp" in data.columns:
        data["order_purchase_timestamp"] = pd.to_datetime(
            data["order_purchase_timestamp"], errors="coerce"
        )
        data = data.dropna(subset=["order_purchase_timestamp"])

    return data.reset_index(drop=True)

if os.path.exists(file_path):
    df_all = load_data(file_path)
else:
    st.error("File main_data.csv tidak ditemukan!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Filter Data")

    min_date = df_all["order_purchase_timestamp"].min().date()
    max_date = df_all["order_purchase_timestamp"].max().date()

    date_range = st.date_input(
        "Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

    all_states = sorted(df_all["customer_state"].dropna().unique())
    selected_states = st.multiselect(
        "Pilih Negara Bagian",
        options=all_states,
        default=all_states
    )

    all_cats = sorted(df_all["product_category_name_english"].dropna().unique())
    selected_categories = st.multiselect(
        "Pilih Kategori",
        options=all_cats,
        default=all_cats[:10]
    )

# --- LOGIKA FILTERING (FINAL - CLOUD SAFE) ---
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

start_dt = pd.Timestamp(start_date)
end_dt = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

main_df = df_all.loc[
    (df_all["order_purchase_timestamp"] >= start_dt) &
    (df_all["order_purchase_timestamp"] <= end_dt)
].copy()

main_df = main_df[main_df["customer_state"].isin(selected_states)]
main_df = main_df[main_df["product_category_name_english"].isin(selected_categories)]

# --- TAMPILAN UTAMA ---
st.title("Analisis Performa E-Commerce Olist 📊")

st.info(
    f"💡 Memuat **{len(main_df)}** baris data dari total **{len(df_all)}** baris data."
)

if not main_df.empty:
    # --- METRICS ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Orders", main_df["order_id"].nunique())
    with m2:
        st.metric("Total Revenue", f"R$ {main_df['price'].sum():,.2f}")
    with m3:
        st.metric("Total Customers", main_df["customer_id"].nunique())

    st.divider()

    # --- VISUALISASI ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top Categories by Revenue")
        top_cat = (
            main_df.groupby("product_category_name_english")["price"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=top_cat,
            x="price",
            y="product_category_name_english",
            ax=ax
        )
        ax.set_xlabel("Total Revenue")
        ax.set_ylabel("Category")
        st.pyplot(fig)

    with c2:
        st.subheader("Top States by Orders")
        state_df = (
            main_df.groupby("customer_state")["order_id"]
            .nunique()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=state_df,
            x="order_id",
            y="customer_state",
            ax=ax
        )
        ax.set_xlabel("Total Orders")
        ax.set_ylabel("State")
        st.pyplot(fig)

else:
    st.warning("Data tidak ditemukan. Silakan sesuaikan filter Anda.")

st.caption("© 2025 - Olist E-Commerce Analysis Dashboard")
