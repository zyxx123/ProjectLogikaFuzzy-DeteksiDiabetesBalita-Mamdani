# -------------------------------------------------------------------
# REFERENSI DATA (STANDAR WHO)
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
