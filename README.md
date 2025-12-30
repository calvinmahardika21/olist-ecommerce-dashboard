# Proyek Analisis Data: E-Commerce Public Dataset (Olist) 🛍️

## Deskripsi Proyek
Proyek ini merupakan bagian dari tugas akhir kelas “Belajar Fundamental Analisis Data” di Dicoding. Fokus utama dari proyek ini adalah melakukan pembersihan data, eksplorasi data, serta visualisasi untuk menggali insight terkait tren penjualan dan perilaku pelanggan menggunakan pendekatan RFM Analysis pada platform e-commerce Olist.

**Judul Proyek:** Analisis Tren Penjualan dan Kepuasan Pelanggan pada Olist E-Commerce

## Struktur Direktori
- `dashboard/`: Berisi aplikasi dashboard interaktif berbasis Streamlit serta dataset yang telah dibersihkan (`main_data.csv`).
- `data/`: Berisi kumpulan dataset mentah dalam format CSV.
- `notebook.ipynb`: Dokumentasi lengkap proses data wrangling, eksplorasi data (EDA), hingga visualisasi.
- `requirements.txt`: Daftar library yang diperlukan untuk menjalankan proyek ini.

## Cara Menjalankan Dashboard
1. Pastikan Python dan seluruh library yang dibutuhkan sudah terpasang. Instalasi dapat dilakukan dengan perintah:
   ```bash
   pip install -r requirements.txt
   ```
2. Jalankan dashboard dengan perintah berikut di terminal:
```bash
streamlit run dashboard/dashboard.py
```