# ATURAN PAKAR (RULE BASE MAMDANI)
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
