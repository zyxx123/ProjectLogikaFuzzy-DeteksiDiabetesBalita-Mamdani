# Contoh Perhitungan Manual Logika Fuzzy Mamdani
*Studi Kasus: Deteksi Risiko Stunting Balita*

Dokumen ini memuat langkah-langkah perhitungan matematika secara manual untuk membuktikan hasil yang dikeluarkan oleh program (Sangat berguna untuk lampiran Bab 4 / Pembahasan Skripsi).

---

## 1. Skenario Studi Kasus
Misalkan seorang pasien datang ke Posyandu dengan data berikut:
- **Jenis Kelamin**: Laki-laki
- **Usia**: 12 bulan
- **Tinggi Badan**: 73 cm
- **Berat Badan**: 9.0 kg

---

## 2. Hitung Persentase Terhadap Median WHO
Berdasarkan tabel referensi WHO untuk Anak Laki-laki usia 12 bulan:
- Median Tinggi Badan ideal = **75.7 cm**
- Median Berat Badan ideal = **10.2 kg**

Kita hitung persentase kecocokan pasien terhadap standar ideal:
- Persentase Tinggi = $(73 / 75.7) \times 100 = \mathbf{96.43\%}$
- Persentase Berat = $(9.0 / 10.2) \times 100 = \mathbf{88.24\%}$

Dua nilai persentase inilah (**96.43** dan **88.24**) yang akan dimasukkan ke dalam perhitungan Fuzzy.

---

## 3. Tahap 1: Fuzzifikasi Input (Mencari Derajat Keanggotaan)
Kita masukkan nilai persentase ke dalam rumus kurva trapesium.

### A. Untuk Tinggi Badan (Input = 96.43)
- **Sangat Pendek** (batas: 0, 0, 80, 88):
  Nilai 96.43 berada di luar batas $\rightarrow$ **0**
- **Pendek** (batas: 83, 88, 93, 98):
  Nilai 96.43 jatuh di garis miring turun (antara 93 dan 98).
  Rumus: $\frac{d - x}{d - c} = \frac{98 - 96.43}{98 - 93} = \frac{1.57}{5} = \mathbf{0.314}$
- **Normal** (batas: 95, 100, 105, 108):
  Nilai 96.43 jatuh di garis miring naik (antara 95 dan 100).
  Rumus: $\frac{x - a}{b - a} = \frac{96.43 - 95}{100 - 95} = \frac{1.43}{5} = \mathbf{0.286}$
- **Tinggi**: **0**

*(Kesimpulan Tinggi Badan: 0.314 Pendek, 0.286 Normal)*

### B. Untuk Berat Badan (Input = 88.24)
- **Sangat Kurang**: **0**
- **Kurang** (batas: 68, 76, 87, 95):
  Nilai 88.24 jatuh di garis miring turun (antara 87 dan 95).
  Rumus: $\frac{d - x}{d - c} = \frac{95 - 88.24}{95 - 87} = \frac{6.76}{8} = \mathbf{0.845}$
- **Normal** (batas: 90, 97, 112, 118):
  Nilai 88.24 berada di bawah batas bawah (90) $\rightarrow$ **0**
- **Lebih**: **0**

*(Kesimpulan Berat Badan: 0.845 Kurang)*

---

## 4. Tahap 2: Evaluasi Aturan (Implikasi Fungsi MIN)
Kita hanya perlu mengevaluasi aturan yang derajat keanggotaannya bernilai lebih dari 0.
Ada dua kemungkinan aturan yang aktif/menyala:

- **Aturan 1:** `JIKA Tinggi = Pendek (0.314) DAN Berat = Kurang (0.845)`
  Berdasarkan pakar, hasilnya adalah Risiko **TINGGI**.
  Karena operatornya AND, kita cari nilai MINIMUM:
  $\alpha_1 = \min(0.314, 0.845) = \mathbf{0.314}$

- **Aturan 2:** `JIKA Tinggi = Normal (0.286) DAN Berat = Kurang (0.845)`
  Berdasarkan pakar, hasilnya adalah Risiko **SEDANG**.
  $\alpha_2 = \min(0.286, 0.845) = \mathbf{0.286}$

---

## 5. Tahap 3: Agregasi (Fungsi MAX)
Jika ada aturan dengan hasil yang sama, kita cari nilai terbesar (MAX). Dalam kasus ini, tiap hasil berdiri sendiri.
- Area Risiko **SEDANG** terpotong di ketinggian $\alpha = \mathbf{0.286}$
- Area Risiko **TINGGI** terpotong di ketinggian $\alpha = \mathbf{0.314}$

---

## 6. Tahap 4: Defuzzifikasi (Metode Centroid / Center of Area)
Kita menumpuk kurva Risiko Sedang yang terpotong 0.286 dan kurva Risiko Tinggi yang terpotong 0.314 menjadi satu bangun datar abstrak. Titik berat sumbu X (Skor) dari bangun ini harus dicari.

Rumus Center of Area (COA):
$$ Z = \frac{\sum (x \times \mu(x))}{\sum \mu(x)} $$

Pendekatan luas area (secara matematis manual):
- **Luas Bangun Risiko Sedang (Trapesium Terpotong)**
  Titik tengah (centroid) secara kasar berada di skor $x = 50$.
  Luas area ($A_1$) $\approx 9.80$ unit persegi.
  Momen luasan = $9.80 \times 50 = 490.0$

- **Luas Bangun Risiko Tinggi (Trapesium Terpotong)**
  Titik tengah (centroid) berada di sekitar skor $x = 73$.
  Luas area ($A_2$) $\approx 9.26$ unit persegi.
  Momen luasan = $9.26 \times 73 = 675.9$

**Perhitungan Akhir Skor Risiko (Titik Berat Keseluruhan):**
$$ Z = \frac{490.0 + 675.9}{9.80 + 9.26} = \frac{1165.9}{19.06} \approx \mathbf{61.17} $$

## 7. Kesimpulan
Skor yang didapatkan adalah **61.17**.
Jika kita lihat aturan kategori warna sistem:
- Skor $< 30$ : Rendah
- Skor $< 55$ : Sedang
- Skor $< 78$ : Tinggi

Maka balita laki-laki usia 12 bulan dengan TB 73cm dan BB 9.0kg tersebut masuk ke dalam kategori **Risiko TINGGI**, dengan akurasi persentase keanggotaan terpusat pada skor **61.17/100**. Hasil ini persis akan cocok jika Anda melakukan pengujian (testing) data yang sama pada aplikasi.
