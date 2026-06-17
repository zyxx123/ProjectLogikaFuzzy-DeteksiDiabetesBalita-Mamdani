import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Fuzzy – Risiko Stunting", page_icon="🔵", layout="centered")

# Memuat file CSS eksternal untuk gaya tampilan
with open("style.css", "r", encoding="utf-8") as file_css:
    st.markdown(f"<style>{file_css.read()}</style>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# BAGIAN 1: REFERENSI DATA (STANDAR WHO)
# -------------------------------------------------------------------
# Data ini berisi: (Umur, TB Laki, BB Laki, TB Perempuan, BB Perempuan)
REFERENSI_WHO = [
    (0,  49.9, 3.3, 49.1, 3.2), (3,  61.4, 6.0, 59.8, 5.6), (6,  67.6, 7.9, 65.7, 7.3),
    (9,  72.3, 9.2, 70.1, 8.6), (12, 75.7,10.2, 74.0, 9.5), (15, 79.1,11.0, 77.5,10.2),
    (18, 82.3,11.7, 80.7,10.8), (21, 85.1,12.3, 83.7,11.4), (24, 87.8,12.7, 86.4,12.1),
    (30, 92.7,14.0, 91.4,13.3), (36, 96.1,14.7, 95.1,14.1), (42, 99.9,15.7, 98.7,14.9),
    (48,103.3,16.7,102.7,15.8), (54,106.7,17.6,106.0,16.8), (60,110.0,18.7,109.4,17.7),
]

def hitung_median_who(usia_bulan, jenis_kelamin):
    """Mencari nilai median standar WHO untuk umur dan jenis kelamin tertentu"""
    index_jk = 0 if jenis_kelamin == "Laki-laki" else 1
    batas_bawah, batas_atas = REFERENSI_WHO[0], REFERENSI_WHO[-1]
    
    # Mencari rentang umur di tabel WHO
    for i in range(len(REFERENSI_WHO)-1):
        if REFERENSI_WHO[i][0] <= usia_bulan <= REFERENSI_WHO[i+1][0]:
            batas_bawah, batas_atas = REFERENSI_WHO[i], REFERENSI_WHO[i+1]
            break
            
    # Rumus interpolasi matematika untuk umur yang berada di tengah-tengah rentang
    jarak_umur = 0 if batas_bawah[0] == batas_atas[0] else (usia_bulan - batas_bawah[0]) / (batas_atas[0] - batas_bawah[0])
    
    median_tinggi = batas_bawah[1 + index_jk * 2] + jarak_umur * (batas_atas[1 + index_jk * 2] - batas_bawah[1 + index_jk * 2])
    median_berat = batas_bawah[2 + index_jk * 2] + jarak_umur * (batas_atas[2 + index_jk * 2] - batas_bawah[2 + index_jk * 2])
    
    return {"tinggi": median_tinggi, "berat": median_berat}

# -------------------------------------------------------------------
# BAGIAN 2: FUNGSI LOGIKA FUZZY (MATEMATIKA)
# -------------------------------------------------------------------

def kurva_trapesium(x, a, b, c, d):
    """Membuat kurva Fuzzy berbentuk Trapesium dengan 4 titik batas"""
    if x <= a or x >= d: 
        return 0.0 # Di luar kurva
    if b <= x <= c:      
        return 1.0 # Puncak kurva (Pasti masuk kategori ini)
    if a < x < b:        
        return (x - a) / (b - a) # Garis miring naik
    return (d - x) / (d - c) # Garis miring turun

def fuzzifikasi_tinggi_badan(persentase):
    """Menghitung seberapa cocok persentase Tinggi Badan masuk ke tiap kategori"""
    return {
        "Sangat Pendek": kurva_trapesium(persentase, 0, 0, 80, 88),
        "Pendek":        kurva_trapesium(persentase, 83, 88, 93, 98),
        "Normal":        kurva_trapesium(persentase, 95, 100, 105, 108),
        "Tinggi":        kurva_trapesium(persentase, 105, 110, 999, 999)
    }

def fuzzifikasi_berat_badan(persentase):
    """Menghitung seberapa cocok persentase Berat Badan masuk ke tiap kategori"""
    return {
        "Sangat Kurang": kurva_trapesium(persentase, 0, 0, 65, 75),
        "Kurang":        kurva_trapesium(persentase, 68, 76, 87, 95),
        "Normal":        kurva_trapesium(persentase, 90, 97, 112, 118),
        "Lebih":         kurva_trapesium(persentase, 113, 120, 999, 999)
    }

def fuzzifikasi_risiko(skor_x):
    """Menentukan kurva output Risiko (dari skor 0 hingga 100)"""
    return {
        "Rendah":        kurva_trapesium(skor_x, 0, 0, 25, 45),
        "Sedang":        kurva_trapesium(skor_x, 30, 50, 50, 70),
        "Tinggi":        kurva_trapesium(skor_x, 55, 75, 75, 90),
        "Sangat Tinggi": kurva_trapesium(skor_x, 80, 90, 100, 100)
    }

# -------------------------------------------------------------------
# BAGIAN 3: ATURAN PAKAR (RULE BASE)
# -------------------------------------------------------------------
ATURAN_FUZZY = [
    # (Kondisi Tinggi, Kondisi Berat, Hasil Risiko)
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
    ("Normal", "Normal", "Rendah"),
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
    # Tahap 1: Evaluasi Aturan (Cari Nilai Minimum / AND) & Agregasi (MAX)
    maksimum_agregasi = {"Rendah": 0.0, "Sedang": 0.0, "Tinggi": 0.0, "Sangat Tinggi": 0.0}
    aturan_aktif = []
    
    for i, (kategori_tinggi, kategori_berat, label_risiko) in enumerate(ATURAN_FUZZY):
        # Implikasi: Ambil nilai terendah (MIN) antara Tinggi dan Berat
        nilai_minimum_alpha = min(derajat_tinggi[kategori_tinggi], derajat_berat[kategori_berat])
        aturan_aktif.append({
            "kategori_tinggi": kategori_tinggi, 
            "kategori_berat": kategori_berat, 
            "label_risiko": label_risiko, 
            "nilai_alpha": nilai_minimum_alpha, 
            "aktif": nilai_minimum_alpha > 0.001
        })
        
        # Agregasi: Ambil nilai tertinggi (MAX) untuk gabungkan area yang sama
        if nilai_minimum_alpha > maksimum_agregasi[label_risiko]:
            maksimum_agregasi[label_risiko] = nilai_minimum_alpha
            
    # Tahap 2: Defuzzifikasi Titik Berat (Centroid / Center of Area)
    pembilang_centroid = 0.0
    penyebut_centroid = 0.0
    titik_skor_x = np.linspace(0, 100, 500) # Membagi rentang skor menjadi 500 titik kecil
    derajat_potongan_kurva = []
    
    for skor_x in titik_skor_x:
        # Cek tinggi kurva output asli pada titik ini
        kurva_output = fuzzifikasi_risiko(skor_x)
        
        nilai_agregasi_tertinggi = 0.0
        for risiko_label in ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]:
            # Potong (clip) kurva output asli dengan batas Agregasi (MIN)
            nilai_terpotong = min(maksimum_agregasi[risiko_label], kurva_output[risiko_label])
            
            # Tumpuk semua kurva yang terpotong menjadi satu bangun ruang luar (MAX)
            if nilai_terpotong > nilai_agregasi_tertinggi:
                nilai_agregasi_tertinggi = nilai_terpotong
                
        # Rumus Center of Gravity: (Luas x Jarak) dibagi (Total Luas)
        pembilang_centroid += skor_x * nilai_agregasi_tertinggi
        penyebut_centroid += nilai_agregasi_tertinggi
        derajat_potongan_kurva.append(nilai_agregasi_tertinggi)
        
    skor_akhir = pembilang_centroid / penyebut_centroid if penyebut_centroid > 0 else 0.0
    return skor_akhir, aturan_aktif, titik_skor_x, derajat_potongan_kurva, maksimum_agregasi

# -------------------------------------------------------------------
# BAGIAN 5: TAMPILAN DAN ANTARMUKA (STREAMLIT)
# -------------------------------------------------------------------

def gaya_tampilan_risiko(skor):
    """Menentukan warna dan teks berdasarkan skor akhir"""
    if skor < 30:  return "✅ Risiko RENDAH",        "#0d2e1a", "#34d399"
    if skor < 55:  return "⚠️ Risiko SEDANG",        "#2d2000", "#fbbf24"
    if skor < 78:  return "🔴 Risiko TINGGI",        "#2d0f0f", "#f87171"
    return            "🚨 Risiko SANGAT TINGGI", "#2a0d1e", "#f472b6"

def daftar_rekomendasi(skor, persentase_tinggi, persentase_berat):
    """Memberikan saran medis berdasarkan hasil analisis"""
    saran = []
    if persentase_tinggi < 90: saran.append("📍 Konsultasi ke Puskesmas/Posyandu untuk pemantauan pertumbuhan rutin.")
    if persentase_berat < 80: saran.append("🥩 Tingkatkan asupan gizi – MPASI berkualitas (protein, zat besi, zinc).")
    if skor >= 55: saran.append("🏥 Anak terindikasi stunting – segera rujuk ke tenaga gizi/dokter anak.")
    if skor >= 78: saran.append("🚨 Periksakan kondisi menyeluruh & laporkan ke program gizi nasional.")
    saran.append("💉 Tetap imunisasi sesuai jadwal dan jaga kebersihan/sanitasi.")
    if skor < 30: saran.append("🌟 Pertumbuhan baik – pertahankan pola makan bergizi seimbang!")
    return saran

st.markdown('<div class="title-badge">🔵 Logika Fuzzy – Mamdani Murni</div>', unsafe_allow_html=True)
st.title("Deteksi Risiko Stunting Balita")
st.caption("Aplikasi ini menggunakan metode Fuzzy Inference System (FIS) tipe Mamdani dengan defuzzifikasi Centroid.")
st.divider()

# Inisialisasi status halaman di Session State
if 'tampilkan_hasil' not in st.session_state:
    st.session_state.tampilkan_hasil = False

if not st.session_state.tampilkan_hasil:
    st.markdown("Silakan masukkan data anak untuk memulai deteksi risiko stunting berdasarkan standar WHO.")
    
    # Kolom Input Form
    kolom_kiri, kolom_kanan = st.columns(2)
    with kolom_kiri:
        # Gunakan session state untuk default value agar nilai sebelumnya tidak hilang saat kembali
        def_usia = st.session_state.get('input_usia', 12)
        def_tinggi = st.session_state.get('input_tinggi', 75.0)
        input_usia   = st.number_input("Usia Anak (bulan)", min_value=0, max_value=60, value=def_usia, step=1)
        input_tinggi = st.number_input("Tinggi Badan (cm)", min_value=30.0, max_value=140.0, value=def_tinggi, step=0.1)
    with kolom_kanan:
        def_jk = st.session_state.get('input_jk', "Laki-laki")
        def_berat = st.session_state.get('input_berat', 9.5)
        jk_index = 0 if def_jk == "Laki-laki" else 1
        input_jk     = st.selectbox("Jenis Kelamin", ["Laki-laki","Perempuan"], index=jk_index)
        input_berat  = st.number_input("Berat Badan (kg)", min_value=1.0, max_value=40.0, value=def_berat, step=0.1)

    st.markdown("")

    # Saat tombol Proses ditekan
    if st.button("🔍 Analisis Risiko Stunting", use_container_width=True, type="primary"):
        # Simpan nilai ke session state
        st.session_state.input_usia = input_usia
        st.session_state.input_tinggi = input_tinggi
        st.session_state.input_jk = input_jk
        st.session_state.input_berat = input_berat
        st.session_state.tampilkan_hasil = True
        st.rerun()

else:
    # -------------------------------------------------------------------
    # HALAMAN HASIL ANALISIS
    # -------------------------------------------------------------------
    input_usia = st.session_state.input_usia
    input_tinggi = st.session_state.input_tinggi
    input_jk = st.session_state.input_jk
    input_berat = st.session_state.input_berat

    if st.button("⬅️ Kembali untuk Deteksi Ulang"):
        st.session_state.tampilkan_hasil = False
        st.rerun()

    # 1. Bandingkan dengan standar WHO
    standar_who = hitung_median_who(input_usia, input_jk)
    persentase_tinggi = (input_tinggi / standar_who["tinggi"]) * 100
    persentase_berat = (input_berat / standar_who["berat"]) * 100
    
    # 2. Proses Fuzzifikasi
    derajat_tinggi = fuzzifikasi_tinggi_badan(persentase_tinggi)
    derajat_berat = fuzzifikasi_berat_badan(persentase_berat)
    
    # 3. Proses Inferensi Mamdani & Defuzzifikasi
    skor_akhir, histori_aturan, kordinat_x, kordinat_y, agregasi = proses_inferensi_mamdani(derajat_tinggi, derajat_berat)
    
    # 4. Tampilkan Hasil
    label_risiko, warna_bg, warna_teks = gaya_tampilan_risiko(skor_akhir)

    st.markdown("---")
    st.subheader("📊 Hasil Analisis")
    st.markdown(f'<div class="result-box" style="background:{warna_bg};color:{warna_teks}">{label_risiko}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="score-info">Skor Titik Berat (Centroid): <b>{skor_akhir:.2f}/100</b> | Tinggi: {input_tinggi}cm ({persentase_tinggi:.1f}% median) | Berat: {input_berat}kg ({persentase_berat:.1f}% median)</div>', unsafe_allow_html=True)
    st.progress(int(skor_akhir))

    # Tampilkan Grafik Area Mamdani
    st.markdown("#### 📈 Visualisasi Kurva Agregasi Mamdani")
    st.caption("Area berwarna menunjukkan ruang himpunan gabungan dari aturan yang menyala. Garis merah adalah titik tengahnya (Nilai Akhir).")
    
    tabel_grafik = pd.DataFrame({'Skor Risiko': kordinat_x, 'Derajat Area': kordinat_y})
    grafik_area = alt.Chart(tabel_grafik).mark_area(opacity=0.5, color='#2dd4bf').encode(
        x=alt.X('Skor Risiko', scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('Derajat Area', scale=alt.Scale(domain=[0, 1]))
    )
    
    if skor_akhir > 0:
        garis_centroid = alt.Chart(pd.DataFrame({'Skor Risiko': [skor_akhir], 'color': ['red']})).mark_rule(color='#f87171', strokeWidth=3).encode(
            x='Skor Risiko'
        )
        st.altair_chart(grafik_area + garis_centroid, use_container_width=True)
    else:
        st.altair_chart(grafik_area, use_container_width=True)

    st.markdown("---")
    st.subheader("🔬 Tinjauan Proses: Nilai Fuzzifikasi")
    kolomA, kolomB = st.columns(2)
    with kolomA:
        st.markdown("**TB/U – Tinggi vs Usia**")
        for kategori, nilai in derajat_tinggi.items():
            st.markdown(f"`{kategori}`"); st.progress(float(nilai), text=f"{nilai*100:.0f}%")
    with kolomB:
        st.markdown("**BB/U – Berat vs Usia**")
        for kategori, nilai in derajat_berat.items():
            st.markdown(f"`{kategori}`"); st.progress(float(nilai), text=f"{nilai*100:.0f}%")

    st.markdown("---")
    st.subheader("⚙️ Tinjauan Proses: Evaluasi Aturan Pakar")
    jumlah_aturan_aktif = sum(1 for rule in histori_aturan if rule["aktif"])
    st.caption(f"{jumlah_aturan_aktif} dari {len(histori_aturan)} aturan ikut menyumbang pembentukan area kurva")
    
    for i, rule in enumerate(histori_aturan):
        kelas_css = "fired" if rule["aktif"] else "notfire"
        ikon = "✅" if rule["aktif"] else "⬜"
        st.markdown(f'<div class="rule-row"><span class="{kelas_css}">{ikon} R{i+1}: JIKA Tinggi=<em>{rule["kategori_tinggi"]}</em> DAN Berat=<em>{rule["kategori_berat"]}</em> MAKA Risiko <b>{rule["label_risiko"]}</b> | alpha={rule["nilai_alpha"]:.3f}</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("💡 Tindak Lanjut & Rekomendasi")
    for saran in daftar_rekomendasi(skor_akhir, persentase_tinggi, persentase_berat):
        st.markdown(f'<div class="rec-item">{saran}</div>', unsafe_allow_html=True)
        
    st.warning("⚠️ Aplikasi sistem pakar ini ditujukan sebagai pendukung keputusan klinis, bukan pengganti diagnosis dokter anak.")
    
    st.markdown("---")
    if st.button("⬅️ Selesai & Kembali", use_container_width=True, type="primary"):
        st.session_state.tampilkan_hasil = False
        st.rerun()
