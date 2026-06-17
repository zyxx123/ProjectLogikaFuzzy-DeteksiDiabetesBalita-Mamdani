# Penjelasan Kode: Algoritma Fuzzy Mamdani Murni

Dokumen ini menjelaskan setiap fungsi dan rumus matematika yang digunakan dalam file `app.py` untuk mendeteksi risiko stunting menggunakan algoritma **Fuzzy Inference System (FIS) Metode Mamdani**. Penamaan variabel dalam kode telah disesuaikan menggunakan bahasa Indonesia agar lebih mudah dipahami.

---

## 1. Fungsi Keanggotaan (Membership Function)

Dalam logika Fuzzy, kita tidak menggunakan nilai mutlak (Hitam/Putih), melainkan derajat keanggotaan antara `0.0` hingga `1.0`. Kode ini menggunakan kurva berbentuk **Trapesium**.

```python
def kurva_trapesium(x, a, b, c, d):
    if x <= a or x >= d: return 0.0          # Di luar kurva (nilai = 0)
    if b <= x <= c:      return 1.0          # Puncak kurva (nilai = 1)
    if a < x < b:        return (x - a)/(b - a)  # Garis miring naik
    return (d - x)/(d - c)                   # Garis miring turun
```
**Penjelasan Rumus:**
- `x` adalah input (misal: persentase tinggi badan).
- `a, b, c, d` adalah titik-titik kordinat yang membentuk trapesium. 
- Jika `x` berada di antara `a` dan `b`, nilainya naik perlahan dari 0 ke 1 dengan rumus $\frac{x-a}{b-a}$.
- Jika `x` berada di antara `c` dan `d`, nilainya turun perlahan dari 1 ke 0 dengan rumus $\frac{d-x}{d-c}$.

---

## 2. Fuzzifikasi Input

Proses ini mengubah nilai tegas (*Crisp Input*) menjadi nilai linguistik (*Fuzzy*). Nilai input (persentase dari standar WHO) dimasukkan ke dalam fungsi `kurva_trapesium` untuk melihat berapa persen dia masuk kategori "Pendek", "Normal", dll.

```python
def fuzzifikasi_tinggi_badan(persentase):
    return {
        "Sangat Pendek": kurva_trapesium(persentase, 0, 0, 80, 88),
        "Pendek":        kurva_trapesium(persentase, 83, 88, 93, 98),
        "Normal":        kurva_trapesium(persentase, 95, 100, 105, 108),
        "Tinggi":        kurva_trapesium(persentase, 105, 110, 999, 999)
    }
```
**Contoh:** Jika input persentase `p = 85`, maka kode di atas akan mengecek:
- Apakah 85 masuk "Sangat Pendek"? (Dihitung pakai batas 0, 0, 80, 88). Hasilnya mungkin `0.375`.
- Apakah 85 masuk "Pendek"? (Dihitung pakai batas 83, 88, 93, 98). Hasilnya mungkin `0.4`.
- Sisanya bernilai `0.0`. 
Hasil output ini berupa *Dictionary* (pasangan antara Nama Kategori dan Derajat Keanggotaannya). Hal yang sama dilakukan pada input Berat Badan (`fuzzifikasi_berat_badan`).

---

## 3. Fuzzifikasi Output

Karena menggunakan **Mamdani Murni**, Output/Keputusan Akhir (Skor 0-100) juga harus berbentuk kurva Fuzzy (bukan nilai konstan/mati).

```python
def fuzzifikasi_risiko(skor_x):
    return {
        "Rendah":        kurva_trapesium(skor_x, 0, 0, 25, 45),
        "Sedang":        kurva_trapesium(skor_x, 30, 50, 50, 70),
        "Tinggi":        kurva_trapesium(skor_x, 55, 75, 75, 90),
        "Sangat Tinggi": kurva_trapesium(skor_x, 80, 90, 100, 100)
    }
```
Ini berarti skor 40 bukan cuma angka 40, tapi merupakan kombinasi antara kategori "Rendah" dan "Sedang".

---

## 4. Inferensi Mamdani (MIN-MAX)

Di sinilah inti dari algoritma Mamdani terjadi. Aturan (`ATURAN_FUZZY`) dievaluasi satu per satu.

### A. Evaluasi Aturan & Implikasi (Fungsi MIN)
Mamdani menggunakan **operator logika AND**. Dalam Fuzzy, operasi `AND` berarti mengambil nilai **minimum** dari kedua himpunan.

```python
    for i, (kategori_tinggi, kategori_berat, label_risiko) in enumerate(ATURAN_FUZZY):
        nilai_minimum_alpha = min(derajat_tinggi[kategori_tinggi], derajat_berat[kategori_berat])
```
- `nilai_minimum_alpha` adalah **Alpha-Predikat (Firing Strength)**.
- Kode ini mencari: Antara keanggotaan Tinggi Badan (`derajat_tinggi`) dan Berat Badan (`derajat_berat`), mana nilai yang paling kecil? Nilai terkecil inilah yang menjadi batasan (*threshold*) seberapa kuat aturan ini berlaku.

### B. Agregasi Aturan (Fungsi MAX)
Dalam Mamdani, jika ada beberapa aturan yang menghasilkan output yang sama (misal ada 3 aturan yang bilang "Sangat Tinggi"), maka kita harus menyatukannya (*Agregasi*) dengan mengambil nilai **maksimum**.

```python
        if nilai_minimum_alpha > maksimum_agregasi[label_risiko]:
            maksimum_agregasi[label_risiko] = nilai_minimum_alpha
```
Variabel `maksimum_agregasi` akan menyimpan puncak tertinggi (potongan tertinggi) dari masing-masing kategori risiko ("Rendah", "Sedang", dll).

---

## 5. Defuzzifikasi (Metode Centroid / Titik Berat)

Tahap terakhir adalah mengubah kembali kurva Fuzzy (hasil Agregasi) menjadi satu angka tegas (Skor 0-100) menggunakan metode **Center of Area (COA)** atau Titik Berat.

Rumus Matematika COA:
$$ Z = \frac{\int \mu(z) \cdot z \, dz}{\int \mu(z) \, dz} $$

Karena kita menggunakan program, perhitungan *Integral* diubah menjadi penjumlahan biasa (*Diskritisasi*), dengan membagi sumbu X menjadi ratusan titik (dalam kode menggunakan 500 titik/`np.linspace(0, 100, 500)`).

```python
    pembilang_centroid = 0.0 # Sigma x * mu(x)
    penyebut_centroid = 0.0  # Sigma mu(x)
    
    # 1. Diskritisasi: pecah garis 0-100 jadi 500 titik kecil
    titik_skor_x = np.linspace(0, 100, 500)
    
    for skor_x in titik_skor_x:
        kurva_output = fuzzifikasi_risiko(skor_x) # 2. Cek kurva output pada titik x ini
        
        nilai_agregasi_tertinggi = 0.0
        for risiko_label in ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]:
            
            # 3. Potong kurva output dengan nilai maksimum agregasi (Implikasi MIN)
            nilai_terpotong = min(maksimum_agregasi[risiko_label], kurva_output[risiko_label])
            
            # 4. Gabungkan semua area yang sudah terpotong (Agregasi MAX)
            if nilai_terpotong > nilai_agregasi_tertinggi:
                nilai_agregasi_tertinggi = nilai_terpotong
                
        # 5. Rumus Titik Berat
        pembilang_centroid += skor_x * nilai_agregasi_tertinggi
        penyebut_centroid += nilai_agregasi_tertinggi
```

**Penjelasan Tahap 5:**
- Kode ini berjalan menyusuri 500 titik koordinat `x` dari kiri ke kanan (Skor 0 hingga Skor 100).
- Di setiap koordinat, kode menghitung `nilai_agregasi_tertinggi` (tinggi kurva agregasi/gabungan pada titik tersebut).
- `pembilang_centroid` mengumpulkan `skor_x * nilai_agregasi_tertinggi` (Jarak $\times$ Tinggi).
- `penyebut_centroid` mengumpulkan `nilai_agregasi_tertinggi` (Luas total area kurva).

**Hasil Akhir:**
```python
    skor_akhir = pembilang_centroid / penyebut_centroid if penyebut_centroid > 0 else 0.0
```
Nilai `skor_akhir` yang dihasilkan ini adalah titik berat dari luasan kurva yang ditampilkan di grafik, dan itulah yang menjadi **Skor Risiko Stunting (0 - 100)** dari sistem Anda.
