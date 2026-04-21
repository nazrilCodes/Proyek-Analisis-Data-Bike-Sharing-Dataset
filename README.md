# Bike Sharing Dashboard
Dashboard interaktif untuk menganalisis data bike sharing dataset.

## Cara Menjalankan

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Jalankan dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

3. **Buka browser:**
   Dashboard akan terbuka di `http://localhost:8501`

## Fitur
- Filter berdasarkan rentang tanggal
- Filter cuaca dan musim
- Perbandingan user type (casual vs registered)
-Visualisasi interaktif:
  - Tren harian
  - Performa musim
  - Pengaruh cuaca
  - Pola hari dalam seminggu
  - Pola jam sibuk
  - Korelasi suhu
  - Distribusi bulanan
  - Heatmap korelasi fitur

## File yang Dibutuhkan
- `all_data_day.csv` - Data harian
- `all_data_hour.csv` - Data per jam

## Lisensi
Copyright (c) Nazril Abi Widiasto 2026