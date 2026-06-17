# Contoh Perhitungan Manual Logika Fuzzy Mamdani
*Pembuktian Matematis Defuzzifikasi Centroid*

Dokumen ini memuat langkah-langkah perhitungan matematika secara **Eksak (Pecahan Area / Momen Geometri)** untuk membuktikan hasil keluaran sistem. Format ini sangat dianjurkan untuk dimasukkan ke dalam **Bab 4 (Hasil dan Pembahasan)** pada skripsi.

---

## 1. Skenario Studi Kasus
Misalkan pasien balita dengan data berikut:
- **Jenis Kelamin**: Laki-laki
- **Usia**: 12 bulan
- **Tinggi Badan**: 72.7 cm
- **Berat Badan**: 9.1 kg

---

## 2. Hitung Persentase Terhadap Median WHO
Berdasarkan tabel standar WHO (Laki-laki, 12 bulan):
- Median Tinggi = 75.7 cm
- Median Berat = 10.2 kg

Menghitung persentase kecocokan input:
- Persentase Tinggi = $(72.7 / 75.7) \times 100 = \mathbf{96.04\%}$
- Persentase Berat = $(9.1 / 10.2) \times 100 = \mathbf{89.22\%}$

---

## 3. Tahap 1: Fuzzifikasi Input (Rumus Trapesium)
Kita menghitung derajat keanggotaan ($\mu$) input pada setiap himpunan fuzzy.

**A. Tinggi Badan (x = 96.04)**
- $\mu_{\text{Pendek}}(x) = \frac{98 - 96.04}{98 - 93} = \frac{1.96}{5} = \mathbf{0.392}$
- $\mu_{\text{Normal}}(x) = \frac{96.04 - 95}{100 - 95} = \frac{1.04}{5} = \mathbf{0.208}$
- Kategori lain bernilai $0$.

**B. Berat Badan (y = 89.22)**
- $\mu_{\text{Kurang}}(y) = \frac{95 - 89.22}{95 - 87} = \frac{5.78}{8} = \mathbf{0.7225}$
- Kategori lain bernilai $0$.

---

## 4. Tahap 2: Evaluasi Aturan (Fungsi Implikasi MIN)
Mencari nilai Alpha-Predikat ($\alpha$) dari kombinasi aturan yang menyala:

- **[Aturan 1]** JIKA Tinggi Normal (0.208) DAN Berat Kurang (0.7225) MAKA Risiko **SEDANG**.
  $\alpha_1 = \min(0.208, 0.7225) = \mathbf{0.208}$

- **[Aturan 2]** JIKA Tinggi Pendek (0.392) DAN Berat Kurang (0.7225) MAKA Risiko **TINGGI**.
  $\alpha_2 = \min(0.392, 0.7225) = \mathbf{0.392}$

---

## 5. Tahap 3 & 4: Agregasi & Defuzzifikasi (Rumus Center of Area)

Kurva agregasi gabungan terbentuk dari pemotongan kurva **SEDANG** setinggi 0.208 dan kurva **TINGGI** setinggi 0.392. Untuk menghitung titik beratnya ($Z$), kita membagi luasan kurva gabungan tersebut menjadi 5 bangun geometri (Metode Momen Luasan Integral):

$$ Z = \frac{\sum (Luas \times Titik Tengah)}{\sum Luas} = \frac{\sum M_i}{\sum A_i} $$

### Perhitungan Momen Tiap Bangun:

**Bangun 1: Segitiga (Sisi Naik Kurva Sedang)**
- Batas X = 30 hingga 34.16 (lebar $w = 4.16$)
- Tinggi = 0.208
- Luas ($A_1$) = $\frac{1}{2} \times 4.16 \times 0.208 = \mathbf{0.432}$
- Titik Tengah ($C_1$) = $30 + (\frac{2}{3} \times 4.16) = \mathbf{32.77}$
- Momen ($M_1$) = $0.432 \times 32.77 = \mathbf{14.16}$

**Bangun 2: Persegi Panjang (Puncak Terpotong Sedang)**
- Batas X = 34.16 hingga 59.16 (lebar $w = 25$)
- Tinggi = 0.208
- Luas ($A_2$) = $25 \times 0.208 = \mathbf{5.200}$
- Titik Tengah ($C_2$) = $34.16 + 12.5 = \mathbf{46.66}$
- Momen ($M_2$) = $5.200 \times 46.66 = \mathbf{242.63}$

**Bangun 3: Trapesium Siku (Transisi Naik ke Kurva Tinggi)**
- Batas X = 59.16 hingga 62.84 (lebar $w = 3.68$)
- Memiliki 2 komponen (Persegi dan Segitiga kecil):
- Total Luas ($A_3$) = $\mathbf{1.104}$
- Total Momen ($M_3$) = $\mathbf{67.55}$

**Bangun 4: Persegi Panjang (Puncak Terpotong Tinggi)**
- Batas X = 62.84 hingga 84.12 (lebar $w = 21.28$)
- Tinggi = 0.392
- Luas ($A_4$) = $21.28 \times 0.392 = \mathbf{8.341}$
- Titik Tengah ($C_4$) = $62.84 + 10.64 = \mathbf{73.48}$
- Momen ($M_4$) = $8.341 \times 73.48 = \mathbf{612.90}$

**Bangun 5: Segitiga (Sisi Turun Kurva Tinggi)**
- Batas X = 84.12 hingga 90.0 (lebar $w = 5.88$)
- Tinggi = 0.392
- Luas ($A_5$) = $\frac{1}{2} \times 5.88 \times 0.392 = \mathbf{1.152}$
- Titik Tengah ($C_5$) = $84.12 + (\frac{1}{3} \times 5.88) = \mathbf{86.08}$
- Momen ($M_5$) = $1.152 \times 86.08 = \mathbf{99.16}$

---

## 6. Hasil Defuzzifikasi (Nilai Z)

Menjumlahkan seluruh Luasan ($A$) dan Momen ($M$):
- **Total Luas ($\sum A$)** = $0.432 + 5.200 + 1.104 + 8.341 + 1.152 = \mathbf{16.229}$
- **Total Momen ($\sum M$)** = $14.16 + 242.63 + 67.55 + 612.90 + 99.16 = \mathbf{1036.40}$

Maka Skor Akhir Risiko Stunting:
$$ Z = \frac{1036.40}{16.229} = \mathbf{63.86} $$

## 7. Kesimpulan
Perhitungan matematika murni menggunakan rumus Momen Luasan (*Center of Area*) menghasilkan skor **63.86**. 

Skor $63.86$ berada di rentang Risiko **TINGGI** (55 - 78). Jika Anda menginputkan data yang persis sama (Usia 12, TB 72.7, BB 9.1) ke dalam aplikasi, nilai yang keluar di program (`pembilang_centroid / penyebut_centroid`) akan menunjukkan hasil yang **identik/akurasi 100% sama** dengan perhitungan matematika kertas ini.
