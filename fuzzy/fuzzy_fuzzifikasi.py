# -------------------------------------------------------------------
# FUNGSI LOGIKA FUZZY (MATEMATIKA)
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
