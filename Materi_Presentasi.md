# Draf Materi Presentasi: Deteksi Risiko Stunting Menggunakan Fuzzy Mamdani

Berikut adalah susunan (outline) per slide yang bisa Anda pindahkan langsung ke Microsoft PowerPoint atau Canva. Teks cetak miring (*italic*) adalah catatan/naskah pembicaraan (Notes) untuk Anda saat presentasi.

---

## Slide 1: Judul
**Deteksi Risiko Stunting Balita Menggunakan Logika Fuzzy Inference System (FIS) Metode Mamdani Murni**
*(Oleh: Nama Anda / Tim Anda)*

> *Catatan bicara: "Selamat pagi bapak/ibu dosen. Hari ini saya akan mendemonstrasikan sistem pakar berbasis AI klasik (Logika Fuzzy) yang saya rancang untuk membantu mendeteksi tingkat risiko stunting pada balita."*

---

## Slide 2: Latar Belakang Masalah
- **Urgensi Stunting:** Stunting adalah malnutrisi kronis yang berdampak fatal pada masa depan perkembangan otak dan fisik balita.
- **Kelemahan Deteksi Manual:** Evaluasi status gizi konvensional terkadang bersifat kaku (hitam/putih) berdasarkan satu garis ambang batas mutlak.
- **Pendekatan Logika Fuzzy:** Dalam ilmu medis, kondisi "Kurang Gizi" atau "Pendek" memiliki area abu-abu (transisi). Fuzzy mampu menghitung *derajat ketidakpastian* (nilai di antara 0 dan 1) sehingga evaluasi lebih fleksibel layaknya pemikiran dokter manusia.

---

## Slide 3: Solusi & Tujuan
- Membangun **Sistem Pendukung Keputusan (SPK)** berbasis web yang dinamis.
- Menerapkan arsitektur **Fuzzy Mamdani Murni**, lengkap dengan visualisasi proses matematis di belakang layar.
- Mengeliminasi sistem "Black-Box" agar hasil komputasi (Skor Risiko 0-100) dapat dipertanggungjawabkan secara rumus matematika kepada tenaga kesehatan.

---

## Slide 4: Standar WHO & Variabel Input
Sistem menggunakan 2 indikator utama kesehatan balita:
1. **TB/U (Tinggi Badan menurut Usia)** $\rightarrow$ Indikator Stunting (Gizi Kronis)
2. **BB/U (Berat Badan menurut Usia)** $\rightarrow$ Indikator Wasting (Gizi Akut)

> *Catatan bicara: "Sistem tidak langsung menggunakan centimeter atau kilogram, melainkan mengubahnya dulu menjadi PERSENTASE KECOCOKAN terhadap Tabel Median WHO 2006 (berdasarkan usia dan gender spesifik)."*

---

## Slide 5: Mengapa Menggunakan Kurva Trapesium?
- Sistem menggunakan fungsi keanggotaan **Kurva Trapesium (Trapezoidal)**, bukan kurva Segitiga atau Gaussian.
- **Alasan Medis:** Kondisi kesehatan (misal: "Tinggi Normal") bukanlah sebuah titik tunggal mutlak, melainkan memiliki *Rentang Toleransi / Core Range* interval yang lebar di mana balita diklasifikasikan 100% normal. Trapesium memfasilitasi "atap/puncak rentang yang datar" ini.

---

## Slide 6: Tahap 1 - Fuzzifikasi (Linguistik)
Transformasi data tegas ke kategori linguistik:
- **Input Tinggi:** Sangat Pendek, Pendek, Normal, Tinggi
- **Input Berat:** Sangat Kurang, Kurang, Normal, Lebih
- **Output Risiko:** Rendah, Sedang, Tinggi, Sangat Tinggi

> *Catatan bicara: "Sebagai bukti penerapan metode Mamdani Asli, variabel Output Keputusan pada sistem kami juga berbentuk KURVA FUZZY berkelanjutan, BUKAN berupa konstanta angka mati (Sugeno)."*

---

## Slide 7: Tahap 2 - Basis Aturan (Rule Base) Pakar
Terdapat 16 kombinasi aturan (Matriks 4x4) untuk merumuskan keparahan.
- Menggunakan Operator Logika **AND**.
- Perhitungan Implikasi menggunakan **Fungsi MINIMUM (MIN)** untuk mencari kekuatan potongan kurva (*Firing Strength / Alpha*).
- **Contoh Aturan:** `JIKA Tinggi = Pendek DAN Berat = Sangat Kurang MAKA Risiko = SANGAT TINGGI`

---

## Slide 8: Tahap 3 & 4 - Inferensi & Defuzzifikasi Centroid
- **Agregasi (Fungsi MAX):** Seluruh kurva risiko yang terpotong disatukan menjadi satu bentuk "Bangun Geometri" abstrak.
- **Defuzzifikasi Center of Area (COA):**
  Mencari Titik Berat (Centroid) dari bangun abstrak tersebut menggunakan rumus Momen Luasan Matematika Eksak.
  $$ Z = \frac{\sum (Luas \times Titik Tengah)}{\sum Luas} $$

---

## Slide 9: Demo Aplikasi & Visualisasi 
*(Di slide ini Anda bisa menampilkan Video/Screenshot aplikasi).*
- **Fitur Unggulan:** Grafik Visualisasi Kurva Agregasi *Real-Time*.
- Area berwarna biru merepresentasikan bentuk gabungan fungsi MAX.
- **Garis Merah Vertikal** membuktikan secara visual letak persisnya titik potong Centroid di sumbu X (sebagai Skor Keputusan).

---

## Slide 10: Kesimpulan
1. Sistem berbasis Logika Fuzzy Mamdani terbukti secara matematis dapat memberikan nilai tingkat keparahan risiko stunting (skor 0-100) secara lebih presisi daripada batas kaku konvensional.
2. Hasil evaluasi program di aplikasi memiliki akurasi 100% identik dengan hasil perhitungan integral momen matematika manual ("di atas kertas").
3. Integrasi perhitungan dengan tampilan visual kurva membuat sistem ini sangat layak dipakai sebagai alat transparan (*white-box*) pendukung bagi dokter anak atau petugas posyandu.
