# Sistem Pakar Deteksi Risiko Stunting Balita (Metode Logika Fuzzy Mamdani)

Aplikasi berbasis web (Flask) yang menerapkan metode Sistem Pakar **Logika Fuzzy Mamdani** untuk mendeteksi tingkat risiko stunting pada balita. Sistem bekerja secara analitik dengan membandingkan data aktual anak (usia, jenis kelamin, tinggi, dan berat) terhadap tabel standar antropometri gizi yang ditetapkan oleh **WHO (World Health Organization)**.

## Fitur Utama
- **Integrasi Standar WHO**: Otomatis menghitung rasio (persentase) menggunakan nilai median tabel gizi WHO melalui teknik Interpolasi Linear (sangat akurat dalam hitungan hari/bulan).
- **Mesin Logika Fuzzy Mamdani**:
  - Fuzzifikasi menggunakan model Kurva Trapesium (Sangat Pendek/Kurang, Pendek, Normal, Tinggi/Lebih).
  - Evaluasi terhadap 16 Aturan Kepakaran medis dasar.
  - Defuzzifikasi berpresisi tinggi dengan teknik Integral *Centroid* (Center of Area).
- **Manajemen Rekam Medis**: *Dashboard* dan basis data MySQL terintegrasi untuk menyimpan riwayat perkembangan pasien (lengkap dengan cetak laporan PDF).
- **Visualisasi Interaktif**: Penggambaran otomatis area kurva pemotongan hasil defuzzifikasi di antarmuka (menggunakan Vega-Lite & JSON).

## Cara Menjalankan Aplikasi (Lokal)

### 1. Persyaratan Sistem
- Python 3.9 atau yang lebih baru.
- MySQL Server (XAMPP / MySQL Workbench).

### 2. Instalasi
Clone repositori ini, kemudian install modul yang dibutuhkan menggunakan command prompt / terminal:

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Database
1. Buka MySQL Anda dan buat database baru.
2. Buka file `database/database.py` dan sesuaikan kredensial koneksi (Host, User, Password, Database Name).
3. Pastikan Anda menjalankan perintah *create table* untuk tabel User (Kader/Admin), tabel Pasien, dan tabel Riwayat Deteksi.

### 4. Eksekusi Program
Jalankan file utama melalui terminal:
```bash
python app.py
```
Aplikasi akan dapat diakses melalui browser pada alamat **`http://localhost:5000`**.

---
*Proyek ini dirancang secara khusus untuk membantu petugas posyandu dan kader kesehatan dalam memberikan indikasi klinis awal terkait gejala Stunting dan Wasting pada balita.*
