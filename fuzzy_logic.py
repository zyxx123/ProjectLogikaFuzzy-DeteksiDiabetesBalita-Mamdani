import numpy as np

# -------------------------------------------------------------------
# BAGIAN 1: REFERENSI DATA (STANDAR WHO)
# -------------------------------------------------------------------
# Tabel standar pertumbuhan anak WHO: (Umur, Median Laki TB, Laki BB, Perempuan TB, Perempuan BB)
REFERENSI_WHO = [
    (0,  49.9, 3.3, 49.1, 3.2), (3,  61.4, 6.0, 59.8, 5.6), (6,  67.6, 7.9, 65.7, 7.3),
    (9,  72.3, 9.2, 70.1, 8.6), (12, 75.7,10.2, 74.0, 9.5), (15, 79.1,11.0, 77.5,10.2),
    (18, 82.3,11.7, 80.7,10.8), (21, 85.1,12.3, 83.7,11.4), (24, 87.8,12.7, 86.4,12.1),
    (30, 92.7,14.0, 91.4,13.3), (36, 96.1,14.7, 95.1,14.1), (42, 99.9,15.7, 98.7,14.9),
    (48,103.3,16.7,102.7,15.8), (54,106.7,17.6,106.0,16.8), (60,110.0,18.7,109.4,17.7),
]

def hitung_median_who(usia_bulan, jenis_kelamin):
    """Mencari median ideal WHO sesuai umur & kelamin dengan interpolasi linear"""
    index_jk = 0 if jenis_kelamin == "Laki-laki" else 1
    batas_bawah, batas_atas = REFERENSI_WHO[0], REFERENSI_WHO[-1]
    
    # Cari 2 titik data WHO terdekat yang mengapit umur pasien
    for i in range(len(REFERENSI_WHO)-1):
        if REFERENSI_WHO[i][0] <= usia_bulan <= REFERENSI_WHO[i+1][0]:
            batas_bawah, batas_atas = REFERENSI_WHO[i], REFERENSI_WHO[i+1]
            break
            
    # Hitung jarak umur pasien di antara 2 titik tersebut (Interpolasi Linear)
    jarak_umur = 0 if batas_bawah[0] == batas_atas[0] else (usia_bulan - batas_bawah[0]) / (batas_atas[0] - batas_bawah[0])
    
    # Hitung estimasi tinggi dan berat median yang akurat
    median_tinggi = batas_bawah[1 + index_jk * 2] + jarak_umur * (batas_atas[1 + index_jk * 2] - batas_bawah[1 + index_jk * 2])
    median_berat = batas_bawah[2 + index_jk * 2] + jarak_umur * (batas_atas[2 + index_jk * 2] - batas_bawah[2 + index_jk * 2])
    
    return {"tinggi": median_tinggi, "berat": median_berat}

# -------------------------------------------------------------------
# BAGIAN 2: FUNGSI LOGIKA FUZZY (MATEMATIKA)
# -------------------------------------------------------------------
def kurva_trapesium(x, a, b, c, d):
    """Membuat fungsi keanggotaan kurva Trapesium (menghitung nilai derajat 0 sampai 1)"""
    if x <= a or x >= d: return 0.0               # Di luar kurva
    if b <= x <= c:      return 1.0               # Di puncak kurva
    if a < x < b:        return (x - a) / (b - a) # Sedang mendaki
    return (d - x) / (d - c)                      # Sedang menurun

def fuzzifikasi_tinggi_badan(persentase):
    """Menerjemahkan persentase tinggi riil ke himpunan linguistik Fuzzy"""
    return {
        "Sangat Pendek": kurva_trapesium(persentase, 0, 0, 80, 88),
        "Pendek":        kurva_trapesium(persentase, 83, 88, 93, 98),
        "Normal":        kurva_trapesium(persentase, 95, 100, 105, 108),
        "Tinggi":        kurva_trapesium(persentase, 105, 110, 999, 999)
    }

def fuzzifikasi_berat_badan(persentase):
    """Menerjemahkan persentase berat riil ke himpunan linguistik Fuzzy"""
    return {
        "Sangat Kurang": kurva_trapesium(persentase, 0, 0, 65, 75),
        "Kurang":        kurva_trapesium(persentase, 68, 76, 87, 95),
        "Normal":        kurva_trapesium(persentase, 90, 97, 112, 118),
        "Lebih":         kurva_trapesium(persentase, 113, 120, 999, 999)
    }

def fuzzifikasi_risiko(skor_x):
    """Batas area himpunan keluaran (Risiko Stunting) dari skor 0 - 100"""
    return {
        "Rendah":        kurva_trapesium(skor_x, 0, 0, 25, 45),
        "Sedang":        kurva_trapesium(skor_x, 30, 50, 50, 70),
        "Tinggi":        kurva_trapesium(skor_x, 55, 75, 75, 90),
        "Sangat Tinggi": kurva_trapesium(skor_x, 80, 90, 100, 100)
    }

# -------------------------------------------------------------------
# BAGIAN 3: ATURAN PAKAR (RULE BASE MAMDANI)
# -------------------------------------------------------------------
# Kumpulan 16 aturan: JIKA (Tinggi) DAN (Berat) MAKA (Risiko)
ATURAN_FUZZY = [
    ("Sangat Pendek", "Sangat Kurang", "Sangat Tinggi"),
    ("Sangat Pendek", "Kurang", "Sangat Tinggi"),
    ("Sangat Pendek", "Normal", "Tinggi"),
    ("Sangat Pendek", "Lebih", "Tinggi"),
    ("Pendek", "Sangat Kurang", "Sangat Tinggi"),
    ("Pendek", "Kurang", "Tinggi"),
    ("Pendek", "Normal", "Sedang"),
    ("Pendek", "Lebih", "Sedang"),
    ("Normal", "Sangat Kurang", "Sedang"),
    ("Normal", "Kurang", "Sedang"),
    ("Normal", "Normal", "Rendah"), # Postur ideal -> Risiko Rendah
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
    # Tempat menyimpan nilai batas atap tertinggi dari tiap label risiko
    maksimum_agregasi = {"Rendah": 0.0, "Sedang": 0.0, "Tinggi": 0.0, "Sangat Tinggi": 0.0}
    aturan_aktif = []
    
    # 1. EVALUASI ATURAN (MAMDANI)
    for i, (kategori_tinggi, kategori_berat, label_risiko) in enumerate(ATURAN_FUZZY):
        # Operator AND = Mengambil nilai minimum dari kedua derajat input
        nilai_minimum_alpha = min(derajat_tinggi[kategori_tinggi], derajat_berat[kategori_berat])
        
        # Menyimpan data aturan yang berjalan (aktif)
        aturan_aktif.append({
            "kategori_tinggi": kategori_tinggi, 
            "kategori_berat": kategori_berat, 
            "label_risiko": label_risiko, 
            "nilai_alpha": nilai_minimum_alpha, 
            "aktif": nilai_minimum_alpha > 0.001
        })
        
        # Agregasi: Ambil nilai maksimal jika ada beberapa aturan yang menghasilkan risiko sama
        if nilai_minimum_alpha > maksimum_agregasi[label_risiko]:
            maksimum_agregasi[label_risiko] = nilai_minimum_alpha
            
    # 2. DEFUZZIFIKASI (METODE CENTROID / TITIK BERAT)
    pembilang_centroid = 0.0
    penyebut_centroid = 0.0
    
    # Membuat 500 titik sampel memanjang (Sumbu X) dari angka 0 hingga 100
    titik_skor_x = np.linspace(0, 100, 500)
    derajat_potongan_kurva = []
    
    # Hitung tinggi area kurva di masing-masing dari 500 titik tersebut
    for skor_x in titik_skor_x:
        kurva_output = fuzzifikasi_risiko(skor_x)
        nilai_agregasi_tertinggi = 0.0
        
        for risiko_label in ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]:
            # Implikasi: Potong bagian atas kurva sesuai nilai agregasi aturan yang menyala
            nilai_terpotong = min(maksimum_agregasi[risiko_label], kurva_output[risiko_label])
            
            # Komposisi: Gabungkan seluruh kurva tersebut menjadi satu bentuk area terluar (MAX)
            if nilai_terpotong > nilai_agregasi_tertinggi:
                nilai_agregasi_tertinggi = nilai_terpotong
                
        # Perhitungan rumus Integral Centroid
        pembilang_centroid += skor_x * nilai_agregasi_tertinggi # Total X * Y
        penyebut_centroid += nilai_agregasi_tertinggi           # Total Area (Y)
        
        derajat_potongan_kurva.append(nilai_agregasi_tertinggi) # Simpan Y untuk menggambar grafik
        
    # Skor Final: Membagi Pembilang dengan Penyebut
    skor_akhir = pembilang_centroid / penyebut_centroid if penyebut_centroid > 0 else 0.0
    
    return skor_akhir, aturan_aktif, titik_skor_x, derajat_potongan_kurva, maksimum_agregasi
