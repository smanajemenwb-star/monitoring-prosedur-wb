# 📋 Monitoring Prosedur – PT WIKA Beton

Dashboard monitoring prosedur sistem manajemen berbasis **Streamlit + Plotly**.

---

## 🚀 Cara Menjalankan

### 1. Install Python (jika belum ada)
Download Python 3.10+ dari https://python.org

### 2. Install dependencies
Buka terminal / command prompt di folder ini, lalu jalankan:

```bash
pip install -r requirements.txt
```

### 3. Jalankan aplikasi
```bash
streamlit run app.py
```

Browser akan otomatis terbuka di `http://localhost:8501`

---

## 📁 Struktur File

```
monitoring_app/
├── app.py            ← kode utama dashboard
├── data.csv          ← data prosedur (89 baris, per 9 Maret 2026)
├── requirements.txt  ← daftar library yang dibutuhkan
└── README.md         ← panduan ini
```

---

## 🔄 Update Data

Untuk update data, edit file `data.csv` dengan kolom:
```
No, Nomor Prosedur, Nama Prosedur, Rev, Kategori, Divisi Pemilik Proses,
Tgl Berlaku, Tgl Review, sisa, Masa Berlaku, Keterangan
```

Kolom **sisa** = jumlah hari tersisa (negatif = sudah expired)  
Kolom **Keterangan** = `Berlaku` atau `Tidak Berlaku`

---

## ✨ Fitur Dashboard

| Tab | Isi |
|-----|-----|
| 📊 Grafik & Analisis | Donut, bar chart, histogram distribusi sisa hari, % berlaku per divisi |
| 📋 Tabel Lengkap | 89 prosedur lengkap dengan search, filter, color coding |
| ⚠️ Peringatan Expired | Alert kritis & segera + timeline chart |
| 🏢 Per Divisi | Ringkasan & detail per divisi, bisa drill-down |
| 🗂️ Per Kategori | Treemap + ringkasan & detail per kategori |

### Filter Sidebar
- Filter per Divisi, Kategori, Status
- Atur threshold peringatan (default 90 hari) dan kritis (default 30 hari)
- Download data hasil filter ke CSV

---

## 🌐 Deploy Online (Gratis)

Untuk bisa diakses tim tanpa install apapun:

1. Upload folder ini ke GitHub
2. Buka https://streamlit.io/cloud
3. Login dengan akun GitHub → klik **New app**
4. Pilih repo dan file `app.py` → klik **Deploy**

Selesai! Dapat URL publik yang bisa dibagikan ke seluruh tim.

---

*PT Wijaya Karya Beton Tbk | DSIM – Kantor Pusat | Form: WB-QMS-PS-01-F08 Rev.02*
