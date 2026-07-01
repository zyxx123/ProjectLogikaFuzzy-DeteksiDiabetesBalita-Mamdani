import numpy as np
from .fuzzy_fuzzifikasi import fuzzifikasi_risiko
from .fuzzy_rules import ATURAN_FUZZY

# -------------------------------------------------------------------
# INFERENSI MAMDANI & DEFUZZIFIKASI
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
