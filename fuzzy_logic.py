import numpy as np

# -------------------------------------------------------------------
# BAGIAN 1: REFERENSI DATA (STANDAR WHO)
# -------------------------------------------------------------------
# Tabel data standar pertumbuhan balita dari WHO (World Health Organization).
# Format setiap baris data: (Umur dalam Bulan, Median Tinggi Laki-laki, Median Berat Laki-laki, Median Tinggi Perempuan, Median Berat Perempuan)
REFERENSI_WHO = [
    (0,  49.9, 3.3, 49.1, 3.2), (3,  61.4, 6.0, 59.8, 5.6), (6,  67.6, 7.9, 65.7, 7.3),
    (9,  72.3, 9.2, 70.1, 8.6), (12, 75.7,10.2, 74.0, 9.5), (15, 79.1,11.0, 77.5,10.2),
    (18, 82.3,11.7, 80.7,10.8), (21, 85.1,12.3, 83.7,11.4), (24, 87.8,12.7, 86.4,12.1),
    (30, 92.7,14.0, 91.4,13.3), (36, 96.1,14.7, 95.1,14.1), (42, 99.9,15.7, 98.7,14.9),
    (48,103.3,16.7,102.7,15.8), (54,106.7,17.6,106.0,16.8), (60,110.0,18.7,109.4,17.7),
]

def hitung_median_who(usia_bulan, jenis_kelamin):
    """Mencari nilai median standar WHO untuk umur dan jenis kelamin tertentu menggunakan metode Interpolasi Linear"""
    # Menentukan indeks untuk pembacaan matriks data: Laki-laki menggunakan basis 0, Perempuan basis 1
    index_jk = 0 if jenis_kelamin == "Laki-laki" else 1
    # Menetapkan batas awal pencarian (data umur terkecil/0 bulan) dan batas akhir (data umur terbesar/60 bulan)
    batas_bawah, batas_atas = REFERENSI_WHO[0], REFERENSI_WHO[-1]
    
    # Mencari dua titik umur standar WHO terdekat yang mengapit (mengurung) umur aktual pasien
    # Contoh: Jika anak berumur 4 bulan, maka batas bawahnya adalah data WHO 3 bulan, dan batas atasnya data WHO 6 bulan.
    for i in range(len(REFERENSI_WHO)-1):
        if REFERENSI_WHO[i][0] <= usia_bulan <= REFERENSI_WHO[i+1][0]:
            batas_bawah, batas_atas = REFERENSI_WHO[i], REFERENSI_WHO[i+1]
            break
            
    # Menghitung rasio matematis/jarak umur anak di antara kedua titik referensi tersebut (Interpolasi Linear).
    # Jika umur pas dengan batas (misal pas 3 bulan), rasionya 0. Jika di tengah-tengah, rasionya proporsional.
    jarak_umur = 0 if batas_bawah[0] == batas_atas[0] else (usia_bulan - batas_bawah[0]) / (batas_atas[0] - batas_bawah[0])
    
    # Menghitung perkiraan nilai Median Tinggi Badan ideal secara spesifik dan akurat untuk anak pada umur tersebut
    median_tinggi = batas_bawah[1 + index_jk * 2] + jarak_umur * (batas_atas[1 + index_jk * 2] - batas_bawah[1 + index_jk * 2])
    # Menghitung perkiraan nilai Median Berat Badan ideal secara spesifik dan akurat untuk anak pada umur tersebut
    median_berat = batas_bawah[2 + index_jk * 2] + jarak_umur * (batas_atas[2 + index_jk * 2] - batas_bawah[2 + index_jk * 2])
    
    # Mengembalikan paket nilai tinggi dan berat ideal yang telah dihitung agar bisa dibandingkan dengan hasil ukur riil
    return {"tinggi": median_tinggi, "berat": median_berat}

# -------------------------------------------------------------------
# BAGIAN 2: FUNGSI LOGIKA FUZZY (MATEMATIKA)
# -------------------------------------------------------------------
def kurva_trapesium(x, a, b, c, d):
    """Fungsi pembentuk grafik derajat keanggotaan Fuzzy berbentuk Trapesium atau Bahu (Shoulder)"""
    # Jika nilai input (X) berada di luar batas kaki kiri (a) atau di luar batas kaki kanan (d), derajatnya mutlak 0.0 (Tidak masuk himpunan)
    if x <= a or x >= d: return 0.0
    # Jika nilai input (X) berada tepat di panggung/atap trapesium (antara b dan c), derajatnya mutlak 1.0 (100% masuk himpunan)
    if b <= x <= c:      return 1.0
    # Jika nilai input (X) sedang mendaki tebing bagian kiri (antara a dan b), hitung rasio pendakiannya
    if a < x < b:        return (x - a) / (b - a)
    # Jika nilai input (X) sedang menuruni jurang bagian kanan (antara c dan d), hitung rasio penurunannya
    return (d - x) / (d - c)

def fuzzifikasi_tinggi_badan(persentase):
    """Proses menerjemahkan angka pasti (persentase kecocokan tinggi aktual dengan ideal WHO) menjadi variabel Linguistik (Bahasa Manusia)"""
    return {
        # Mengukur derajat kecocokan (0.0 sampai 1.0) tinggi pasien ke dalam kategori "Sangat Pendek" (Trapesium Bahu Kiri)
        "Sangat Pendek": kurva_trapesium(persentase, 0, 0, 80, 88),
        # Mengukur derajat kecocokan tinggi pasien ke dalam kategori "Pendek" (Trapesium Segitiga Tengah)
        "Pendek":        kurva_trapesium(persentase, 83, 88, 93, 98),
        # Mengukur derajat kecocokan tinggi pasien ke dalam kategori "Normal" (Trapesium Segitiga Tengah)
        "Normal":        kurva_trapesium(persentase, 95, 100, 105, 108),
        # Mengukur derajat kecocokan tinggi pasien ke dalam kategori "Tinggi" (Trapesium Bahu Kanan). Angka 999 mewakili jarak tak terhingga.
        "Tinggi":        kurva_trapesium(persentase, 105, 110, 999, 999)
    }

def fuzzifikasi_berat_badan(persentase):
    """Proses menerjemahkan angka pasti (persentase kecocokan berat aktual dengan ideal WHO) menjadi himpunan Fuzzy"""
    return {
        # Menghitung nilai keanggotaan untuk label "Sangat Kurang"
        "Sangat Kurang": kurva_trapesium(persentase, 0, 0, 65, 75),
        # Menghitung nilai keanggotaan untuk label "Kurang"
        "Kurang":        kurva_trapesium(persentase, 68, 76, 87, 95),
        # Menghitung nilai keanggotaan untuk label "Normal"
        "Normal":        kurva_trapesium(persentase, 90, 97, 112, 118),
        # Menghitung nilai keanggotaan untuk label "Lebih / Overweight"
        "Lebih":         kurva_trapesium(persentase, 113, 120, 999, 999)
    }

def fuzzifikasi_risiko(skor_x):
    """Fungsi penentu batas wilayah (domain) untuk setiap Kurva Keluaran (Output) Skor Risiko Stunting dari range nilai 0 hingga 100"""
    return {
        "Rendah":        kurva_trapesium(skor_x, 0, 0, 25, 45),    # Area Risiko Rendah (Kurva Bahu Kiri)
        "Sedang":        kurva_trapesium(skor_x, 30, 50, 50, 70),  # Area Risiko Sedang (Kurva Tengah)
        "Tinggi":        kurva_trapesium(skor_x, 55, 75, 75, 90),  # Area Risiko Tinggi (Kurva Tengah)
        "Sangat Tinggi": kurva_trapesium(skor_x, 80, 90, 100, 100) # Area Risiko Sangat Tinggi (Kurva Bahu Kanan)
    }

# -------------------------------------------------------------------
# BAGIAN 3: ATURAN PAKAR (RULE BASE MAMDANI)
# -------------------------------------------------------------------
# Kumpulan aturan nalar "JIKA (Tinggi) DAN (Berat) MAKA (Risiko)".
# Ini adalah otak utama (Knowledge Base) sistem pakar yang dirancang untuk meniru pola pikir diagnosa dokter/ahli gizi.
# Terdiri dari 16 permutasi total (Kombinasi 4 kategori Tinggi dengan 4 kategori Berat).
ATURAN_FUZZY = [
    ("Sangat Pendek", "Sangat Kurang", "Sangat Tinggi"), # JIKA Tinggi SANGAT PENDEK dan Berat SANGAT KURANG, MAKA Risiko SANGAT TINGGI
    ("Sangat Pendek", "Kurang", "Sangat Tinggi"),        # JIKA Tinggi SANGAT PENDEK dan Berat KURANG, MAKA Risiko SANGAT TINGGI
    ("Sangat Pendek", "Normal", "Tinggi"),               # JIKA Tinggi SANGAT PENDEK dan Berat NORMAL, MAKA Risiko TINGGI (Stunting namun tidak kurus)
    ("Sangat Pendek", "Lebih", "Tinggi"),
    ("Pendek", "Sangat Kurang", "Sangat Tinggi"),
    ("Pendek", "Kurang", "Tinggi"),                      # JIKA Tinggi PENDEK dan Berat KURANG, MAKA Risiko TINGGI
    ("Pendek", "Normal", "Sedang"),
    ("Pendek", "Lebih", "Sedang"),
    ("Normal", "Sangat Kurang", "Sedang"),
    ("Normal", "Kurang", "Sedang"),
    ("Normal", "Normal", "Rendah"),                      # JIKA postur tubuh NORMAL secara proporsional secara keseluruhan, MAKA Risiko RENDAH (Aman)
    ("Normal", "Lebih", "Rendah"),
    ("Tinggi", "Sangat Kurang", "Sedang"),
    ("Tinggi", "Kurang", "Rendah"),
    ("Tinggi", "Normal", "Rendah"),
    ("Tinggi", "Lebih", "Rendah"),
]

# -------------------------------------------------------------------
# BAGIAN 4: INFERENSI MAMDANI & DEFUZZIFIKASI
# -------------------------------------------------------------------
def proses_inferensi_mamdani(derajat_tinggi, derajat_berat):
    # 1. Menyiapkan kamus/tempat untuk menyimpan nilai agregasi (gabungan) tertinggi dari setiap label risiko. Awalnya diatur 0.
    maksimum_agregasi = {"Rendah": 0.0, "Sedang": 0.0, "Tinggi": 0.0, "Sangat Tinggi": 0.0}
    # 2. Membuat daftar kosong untuk menyimpan jejak atau riwayat aturan mana saja yang terpanggil (aktif)
    aturan_aktif = []
    
    # 3. Looping (perulangan) untuk mengevaluasi semua 16 Aturan Pakar (JIKA ... DAN ... MAKA ...) satu per satu
    for i, (kategori_tinggi, kategori_berat, label_risiko) in enumerate(ATURAN_FUZZY):
        # 4. Menerapkan operasi logika AND (irisan). Dalam Fuzzy Mamdani, operator AND berarti mengambil nilai yang paling KECIL (min) dari dua parameter input.
        nilai_minimum_alpha = min(derajat_tinggi[kategori_tinggi], derajat_berat[kategori_berat])
        
        # 5. Mencatat riwayat evaluasi setiap aturan ke dalam daftar (untuk ditampilkan di bagian "Detail Perhitungan" pada website)
        aturan_aktif.append({
            "kategori_tinggi": kategori_tinggi, 
            "kategori_berat": kategori_berat, 
            "label_risiko": label_risiko, 
            "nilai_alpha": nilai_minimum_alpha, 
            "aktif": nilai_minimum_alpha > 0.001 # 6. Suatu aturan dianggap "menyala" (aktif) jika nilai keanggotaannya lebih besar dari 0
        })
        
        # 7. Tahap Agregasi (Penggabungan Aturan dengan operator Maksimum): 
        # Jika ada beberapa aturan yang menghasilkan label risiko yang SAMA (misal ada 3 aturan yang bilang "Sedang"),
        # maka kita hanya akan mengambil nilai simpulan (alpha) yang paling BESAR (maksimum) di antara ketiganya.
        if nilai_minimum_alpha > maksimum_agregasi[label_risiko]:
            maksimum_agregasi[label_risiko] = nilai_minimum_alpha
            
    # 8. Tahap Defuzzifikasi menggunakan metode Centroid (Mencari Titik Berat)
    # Menyiapkan variabel untuk menjumlahkan hasil perkalian (skor * luas area) sebagai 'pembilang' rumus Centroid
    pembilang_centroid = 0.0
    # Menyiapkan variabel untuk menjumlahkan total luas area sebagai 'penyebut' rumus Centroid
    penyebut_centroid = 0.0
    
    # 9. Karena rumus Centroid sebenarnya adalah Integral (kalkulus), kita menghitungnya dengan memotong-motong area (pendekatan diskrit).
    # Disini kita membuat 500 titik potong/sampel secara merata dari skor 0 hingga 100 untuk sumbu mendatar (Sumbu X)
    titik_skor_x = np.linspace(0, 100, 500)
    # Tempat penampungan hasil perhitungan bentuk kurva akhir untuk keperluan menggambar grafik
    derajat_potongan_kurva = []
    
    # 10. Melakukan perulangan perhitungan pada ke-500 titik potongan (dari skor 0 sampai 100)
    for skor_x in titik_skor_x:
        # a. Mengecek nilai/ketinggian kurva trapesium asli (Risiko Rendah, Sedang, Tinggi) pada titik X saat ini
        kurva_output = fuzzifikasi_risiko(skor_x)
        # b. Variabel untuk mencatat titik tertinggi kurva gabungan pada titik X ini
        nilai_agregasi_tertinggi = 0.0
        
        # c. Memproses gabungan keempat kurva (Rendah, Sedang, Tinggi, Sangat Tinggi) menjadi satu kurva agregasi
        for risiko_label in ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]:
            # d. Operasi Implikasi Mamdani: Memotong ("clipping") bagian atap kurva trapesium.
            # Bentuk keluaran dipotong secara horizontal sehingga tingginya tidak melebihi nilai maksimal dari aturan yang aktif (maksimum_agregasi).
            nilai_terpotong = min(maksimum_agregasi[risiko_label], kurva_output[risiko_label])
            
            # e. Operasi Komposisi Aturan: Menumpuk seluruh kurva terpotong tadi menjadi sebuah himpunan area tunggal yang luas.
            # Menggunakan batasan luar/tertinggi (operator UNION/Maksimum).
            if nilai_terpotong > nilai_agregasi_tertinggi:
                nilai_agregasi_tertinggi = nilai_terpotong
                
        # 11. Memasukkan perhitungan area pada titik ini ke dalam rumus sigma Defuzzifikasi Centroid:
        # Menambahkan (titik Sumbu X) * (ketinggian Area Y) ke dalam total pembilang
        pembilang_centroid += skor_x * nilai_agregasi_tertinggi
        # Menambahkan ketinggian Area Y ke dalam total penyebut
        penyebut_centroid += nilai_agregasi_tertinggi
        # 12. Menyimpan rekam jejak ketinggian area Y agar bisa divisualisasikan menjadi diagram di website
        derajat_potongan_kurva.append(nilai_agregasi_tertinggi)
        
    # 13. Rumus akhir Centroid: membagi total momen area dengan total pembobot luasan area (Z* = Σx·µ(x) / Σµ(x))
    # Jika penyebut > 0 (berarti bentuk areanya ada), lakukan pembagian. Jika 0 (tidak ada aturan aktif), beri skor 0.
    skor_akhir = pembilang_centroid / penyebut_centroid if penyebut_centroid > 0 else 0.0
    
    # 14. Mengirimkan seluruh hasil perhitungan akhir ke fungsi utama untuk ditampilkan
    return skor_akhir, aturan_aktif, titik_skor_x, derajat_potongan_kurva, maksimum_agregasi
