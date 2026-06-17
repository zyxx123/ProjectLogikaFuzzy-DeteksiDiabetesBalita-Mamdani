# Penjelasan Kode: Algoritma Fuzzy Mamdani Murni

Dokumen ini menjelaskan setiap fungsi dan rumus matematika yang digunakan dalam file `app.py` untuk mendeteksi risiko stunting menggunakan algoritma **Fuzzy Inference System (FIS) Metode Mamdani**.

---

## 1. Fungsi Keanggotaan (Membership Function)

Dalam logika Fuzzy, kita tidak menggunakan nilai mutlak (Hitam/Putih), melainkan derajat keanggotaan antara `0.0` hingga `1.0`. Kode ini menggunakan kurva berbentuk **Trapesium**.

```python
def trapesium(x, a, b, c, d):
    if x<=a or x>=d: return 0.0          # Di luar kurva (nilai = 0)
    if b<=x<=c:      return 1.0          # Puncak kurva (nilai = 1)
    if a<x<b:        return (x-a)/(b-a)  # Garis miring naik
    return (d-x)/(d-c)                   # Garis miring turun
```
**Penjelasan Rumus:**
- `x` adalah input (misal: persentase tinggi badan).
- `a, b, c, d` adalah titik-titik kordinat yang membentuk trapesium. 
- Jika `x` berada di antara `a` dan `b`, nilainya naik perlahan dari 0 ke 1 dengan rumus $\frac{x-a}{b-a}$.
- Jika `x` berada di antara `c` dan `d`, nilainya turun perlahan dari 1 ke 0 dengan rumus $\frac{d-x}{d-c}$.

---

## 2. Fuzzifikasi Input

Proses ini mengubah nilai tegas (*Crisp Input*) menjadi nilai linguistik (*Fuzzy*). Nilai input (persentase dari standar WHO) dimasukkan ke dalam fungsi `trapesium` untuk melihat berapa persen dia masuk kategori "Pendek", "Normal", dll.

```python
def fuzz_tb(p):
    return {
        "Sangat Pendek": trapesium(p, 0, 0, 80, 88),
        "Pendek":        trapesium(p, 83, 88, 93, 98),
        "Normal":        trapesium(p, 95, 100, 105, 108),
        "Tinggi":        trapesium(p, 105, 110, 999, 999)
    }
```
**Contoh:** Jika input persentase `p = 85`, maka kode di atas akan mengecek:
- Apakah 85 masuk "Sangat Pendek"? (Dihitung pakai batas 0, 0, 80, 88). Hasilnya mungkin `0.375`.
- Apakah 85 masuk "Pendek"? (Dihitung pakai batas 83, 88, 93, 98). Hasilnya mungkin `0.4`.
- Sisanya bernilai `0.0`. 
Hasil output ini berupa *Dictionary* (pasangan antara Nama Kategori dan Derajat Keanggotaannya). Hal yang sama dilakukan pada input Berat Badan (`fuzz_bb`).

---

## 3. Fuzzifikasi Output

Karena menggunakan **Mamdani Murni**, Output/Keputusan Akhir (Skor 0-100) juga harus berbentuk kurva Fuzzy (bukan nilai konstan/mati).

```python
def fuzz_risiko(x):
    return {
        "Rendah":        trapesium(x, 0, 0, 25, 45),
        "Sedang":        trapesium(x, 30, 50, 50, 70),
        "Tinggi":        trapesium(x, 55, 75, 75, 90),
        "Sangat Tinggi": trapesium(x, 80, 90, 100, 100)
    }
```
Ini berarti skor 40 bukan cuma angka 40, tapi merupakan kombinasi antara kategori "Rendah" dan "Sedang".

---

## 4. Inferensi Mamdani (MIN-MAX)

Di sinilah inti dari algoritma Mamdani terjadi. Aturan (*RULES*) dievaluasi satu per satu.

### A. Evaluasi Aturan & Implikasi (Fungsi MIN)
Mamdani menggunakan **operator logika AND**. Dalam Fuzzy, operasi `AND` berarti mengambil nilai **minimum** dari kedua himpunan.

```python
    for i, (tc, bc, risiko) in enumerate(RULES):
        w = min(tb_mem[tc], bb_mem[bc])
```
- `w` adalah **Alpha-Predikat (Firing Strength)**.
- Kode ini mencari: Antara keanggotaan Tinggi Badan (`tb_mem`) dan Berat Badan (`bb_mem`), mana nilai yang paling kecil? Nilai terkecil inilah yang menjadi batasan (*threshold*) seberapa kuat aturan ini berlaku.

### B. Agregasi Aturan (Fungsi MAX)
Dalam Mamdani, jika ada beberapa aturan yang menghasilkan output yang sama (misal ada 3 aturan yang bilang "Sangat Tinggi"), maka kita harus menyatukannya (*Agregasi*) dengan mengambil nilai **maksimum**.

```python
        if w > alpha_max[risiko]:
            alpha_max[risiko] = w
```
Variabel `alpha_max` akan menyimpan puncak tertinggi (potongan tertinggi) dari masing-masing kategori risiko ("Rendah", "Sedang", dll).

---

## 5. Defuzzifikasi (Metode Centroid / Titik Berat)

Tahap terakhir adalah mengubah kembali kurva Fuzzy (hasil Agregasi) menjadi satu angka tegas (Skor 0-100) menggunakan metode **Center of Area (COA)** atau Titik Berat.

Rumus Matematika COA:
$$ Z = \frac{\int \mu(z) \cdot z \, dz}{\int \mu(z) \, dz} $$

Karena kita menggunakan program, perhitungan *Integral* diubah menjadi penjumlahan biasa (*Diskritisasi*), dengan membagi sumbu X menjadi ratusan titik (dalam kode menggunakan 500 titik/`np.linspace(0, 100, 500)`).

```python
    num = 0.0 # Pembilang (Sigma x * mu(x))
    den = 0.0 # Penyebut (Sigma mu(x))
    
    # 1. Diskritisasi: pecah garis 0-100 jadi 500 titik kecil
    x_points = np.linspace(0, 100, 500)
    
    for x in x_points:
        mem = fuzz_risiko(x) # 2. Cek kurva output pada titik x ini
        
        agg_val = 0.0
        for risiko_label in ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]:
            
            # 3. Potong kurva output dengan alpha_max (Implikasi MIN)
            clipped_val = min(alpha_max[risiko_label], mem[risiko_label])
            
            # 4. Gabungkan semua area yang sudah terpotong (Agregasi MAX)
            if clipped_val > agg_val:
                agg_val = clipped_val
                
        # 5. Rumus Titik Berat
        num += x * agg_val
        den += agg_val
```

**Penjelasan Tahap 5:**
- Kode ini berjalan menyusuri 500 titik koordinat `x` dari kiri ke kanan (Skor 0 hingga Skor 100).
- Di setiap koordinat, kode menghitung `agg_val` (tinggi kurva agregasi/gabungan pada titik tersebut).
- `num` (Pembilang) mengumpulkan `x * agg_val` (Jarak $\times$ Tinggi).
- `den` (Penyebut) mengumpulkan `agg_val` (Luas total area kurva).

**Hasil Akhir:**
```python
    score = num / den if den > 0 else 0.0
```
Nilai `score` yang dihasilkan ini adalah titik berat dari luasan kurva yang ditampilkan di grafik, dan itulah yang menjadi **Skor Risiko Stunting (0 - 100)** dari sistem Anda.
