import streamlit as st
import pandas as pd
import altair as alt
from database import *
from fuzzy_logic import *

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Fuzzy – Risiko Stunting", page_icon="🔵", layout="wide")

# Memuat file CSS eksternal untuk gaya tampilan
try:
    with open("style.css", "r", encoding="utf-8") as file_css:
        st.markdown(f"<style>{file_css.read()}</style>", unsafe_allow_html=True)
except:
    pass

# Inisialisasi Database
if 'db_terinisialisasi' not in st.session_state:
    sukses = inisialisasi_database()
    st.session_state.db_terinisialisasi = sukses
    if not sukses:
        st.error("Gagal terhubung ke database MySQL. Pastikan XAMPP/Laragon menyala.")

# Session State untuk Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# --- HALAMAN LOGIN ---
def halaman_login():
    st.markdown('<div class="title-badge">🔵 Sistem Pakar Stunting Terpadu</div>', unsafe_allow_html=True)
    st.title("Login Sistem")
    
    with st.form("form_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Masuk", use_container_width=True)
        
        if submit:
            user = verifikasi_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_data = user
                st.success(f"Login berhasil sebagai {user['role']}!")
                st.rerun()
            else:
                st.error("Username atau password salah!")

    st.info("Akun Default Administrator: username `admin`, password `admin123`\n\nAkun Default Pengguna (Kader): username `kader`, password `kader123`")

# --- KOMPONEN BANTUAN UI ---
def gaya_tampilan_risiko(skor):
    if skor < 30:  return "✅ Risiko RENDAH",        "#0d2e1a", "#34d399"
    if skor < 55:  return "⚠️ Risiko SEDANG",        "#2d2000", "#fbbf24"
    if skor < 78:  return "🔴 Risiko TINGGI",        "#2d0f0f", "#f87171"
    return            "🚨 Risiko SANGAT TINGGI", "#2a0d1e", "#f472b6"

def daftar_rekomendasi(skor, persentase_tinggi, persentase_berat):
    saran = []
    if persentase_tinggi < 90: saran.append("📍 Konsultasi ke Puskesmas/Posyandu untuk pemantauan pertumbuhan rutin.")
    if persentase_berat < 80: saran.append("🥩 Tingkatkan asupan gizi – MPASI berkualitas (protein, zat besi, zinc).")
    if skor >= 55: saran.append("🏥 Anak terindikasi stunting – segera rujuk ke tenaga gizi/dokter anak.")
    if skor >= 78: saran.append("🚨 Periksakan kondisi menyeluruh & laporkan ke program gizi nasional.")
    saran.append("💉 Tetap imunisasi sesuai jadwal dan jaga kebersihan/sanitasi.")
    if skor < 30: saran.append("🌟 Pertumbuhan baik – pertahankan pola makan bergizi seimbang!")
    return saran

# --- HALAMAN MANAJEMEN PASIEN ---
def halaman_manajemen_pasien():
    st.header("Manajemen Data Pasien")
    tab1, tab2 = st.tabs(["Daftar Pasien", "Tambah Pasien Baru"])
    
    with tab1:
        pasien = dapatkan_semua_pasien()
        if pasien:
            df = pd.DataFrame(pasien)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada data pasien.")
            
    with tab2:
        with st.form("form_tambah_pasien"):
            nama = st.text_input("Nama Anak")
            jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            tgl_lahir = st.date_input("Tanggal Lahir")
            nama_ortu = st.text_input("Nama Orang Tua")
            if st.form_submit_button("Simpan Pasien"):
                if nama and nama_ortu:
                    tambah_pasien(nama, jk, tgl_lahir, nama_ortu)
                    st.success("Pasien berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("Mohon lengkapi semua data.")

# --- HALAMAN DETEKSI (PENGGUNA) ---
def halaman_deteksi():
    st.header("Deteksi Risiko Stunting")
    
    pasien_list = dapatkan_semua_pasien()
    if not pasien_list:
        st.warning("Belum ada data pasien. Silakan tambahkan pasien terlebih dahulu di menu Manajemen Pasien.")
        return
        
    pilihan_pasien = st.selectbox(
        "Pilih Pasien", 
        options=pasien_list, 
        format_func=lambda x: f"{x['nama_anak']} ({x['jenis_kelamin']}) - Anak dari {x['nama_orang_tua']}"
    )
    
    if 'tampilkan_hasil' not in st.session_state:
        st.session_state.tampilkan_hasil = False

    if not st.session_state.tampilkan_hasil:
        kolom_kiri, kolom_kanan = st.columns(2)
        with kolom_kiri:
            input_usia = st.number_input("Usia Anak (bulan)", min_value=0, max_value=60, value=12, step=1)
            input_tinggi = st.number_input("Tinggi Badan (cm)", min_value=30.0, max_value=140.0, value=75.0, step=0.1)
        with kolom_kanan:
            input_berat  = st.number_input("Berat Badan (kg)", min_value=1.0, max_value=40.0, value=9.5, step=0.1)

        if st.button("🔍 Analisis & Simpan Hasil", use_container_width=True, type="primary"):
            st.session_state.input_usia = input_usia
            st.session_state.input_tinggi = input_tinggi
            st.session_state.input_berat = input_berat
            st.session_state.pasien_terpilih = pilihan_pasien
            st.session_state.tampilkan_hasil = True
            st.rerun()
    else:
        # Proses Hasil Deteksi
        if st.button("⬅️ Kembali untuk Deteksi Ulang"):
            st.session_state.tampilkan_hasil = False
            st.rerun()

        pasien = st.session_state.pasien_terpilih
        input_usia = st.session_state.input_usia
        input_tinggi = st.session_state.input_tinggi
        input_berat = st.session_state.input_berat
        
        standar_who = hitung_median_who(input_usia, pasien['jenis_kelamin'])
        persentase_tinggi = (input_tinggi / standar_who["tinggi"]) * 100
        persentase_berat = (input_berat / standar_who["berat"]) * 100
        
        derajat_tinggi = fuzzifikasi_tinggi_badan(persentase_tinggi)
        derajat_berat = fuzzifikasi_berat_badan(persentase_berat)
        
        skor_akhir, histori_aturan, kordinat_x, kordinat_y, agregasi = proses_inferensi_mamdani(derajat_tinggi, derajat_berat)
        label_risiko, warna_bg, warna_teks = gaya_tampilan_risiko(skor_akhir)

        # SIMPAN KE DATABASE SEKALI SAJA
        if 'sudah_disimpan' not in st.session_state:
            bersih_label = label_risiko.split("Risiko ")[-1]
            simpan_riwayat(pasien['id'], input_usia, input_tinggi, input_berat, skor_akhir, bersih_label, st.session_state.user_data['id'])
            st.session_state.sudah_disimpan = True
            st.success("Hasil berhasil disimpan ke dalam database riwayat!")

        st.markdown("---")
        st.subheader(f"📊 Hasil Analisis: {pasien['nama_anak']}")
        st.markdown(f'<div class="result-box" style="background:{warna_bg};color:{warna_teks}">{label_risiko}</div>', unsafe_allow_html=True)
        st.progress(int(skor_akhir), text=f"Skor Titik Berat (Centroid): {skor_akhir:.2f}/100")
        
        # Grafik
        tabel_grafik = pd.DataFrame({'Skor Risiko': kordinat_x, 'Derajat Area': kordinat_y})
        grafik_area = alt.Chart(tabel_grafik).mark_area(opacity=0.5, color='#2dd4bf').encode(
            x=alt.X('Skor Risiko', scale=alt.Scale(domain=[0, 100])),
            y=alt.Y('Derajat Area', scale=alt.Scale(domain=[0, 1]))
        )
        if skor_akhir > 0:
            garis_centroid = alt.Chart(pd.DataFrame({'Skor Risiko': [skor_akhir], 'color': ['red']})).mark_rule(color='#f87171', strokeWidth=3).encode(x='Skor Risiko')
            st.altair_chart(grafik_area + garis_centroid, use_container_width=True)
        else:
            st.altair_chart(grafik_area, use_container_width=True)

        if st.button("⬅️ Selesai"):
            st.session_state.tampilkan_hasil = False
            if 'sudah_disimpan' in st.session_state: del st.session_state.sudah_disimpan
            st.rerun()

# --- HALAMAN DASHBOARD (ADMIN) ---
def halaman_dashboard():
    st.header("Dashboard Statistik Stunting")
    riwayat = dapatkan_semua_riwayat()
    
    if riwayat:
        df = pd.DataFrame(riwayat)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pemeriksaan", len(df))
        col2.metric("Sangat Tinggi / Tinggi", len(df[df['label_risiko'].isin(['TINGGI', 'SANGAT TINGGI'])]))
        col3.metric("Normal / Rendah", len(df[df['label_risiko'] == 'RENDAH']))
        
        st.subheader("Seluruh Riwayat Pemeriksaan")
        # Format tabel agar rapi
        df_show = df[['tanggal_periksa', 'nama_anak', 'usia_bulan', 'tinggi_cm', 'berat_kg', 'label_risiko', 'nama_petugas']]
        st.dataframe(df_show, use_container_width=True)
    else:
        st.info("Belum ada data pemeriksaan.")

# --- ROUTER UTAMA ---
if not st.session_state.logged_in:
    halaman_login()
else:
    user = st.session_state.user_data
    
    with st.sidebar:
        st.markdown(f"### Halo, {user['username']}!")
        st.caption(f"Role: {user['role'].upper()}")
        st.divider()
        
        if user['role'] == 'admin':
            menu = st.radio("Navigasi", ["Dashboard Statistik", "Manajemen Pasien"])
        else:
            menu = st.radio("Navigasi", ["Deteksi Risiko", "Manajemen Pasien", "Riwayat Seluruh Pasien"])
            
        st.divider()
        if st.button("🚪 Keluar (Logout)"):
            st.session_state.clear()
            st.rerun()
            
    # Tampilkan Halaman Sesuai Menu
    if user['role'] == 'admin':
        if menu == "Dashboard Statistik": halaman_dashboard()
        elif menu == "Manajemen Pasien": halaman_manajemen_pasien()
    else:
        if menu == "Deteksi Risiko": halaman_deteksi()
        elif menu == "Manajemen Pasien": halaman_manajemen_pasien()
        elif menu == "Riwayat Seluruh Pasien":
            st.header("Riwayat Seluruh Pasien")
            riwayat = dapatkan_semua_riwayat()
            if riwayat: st.dataframe(pd.DataFrame(riwayat)[['tanggal_periksa', 'nama_anak', 'usia_bulan', 'tinggi_cm', 'berat_kg', 'skor_fuzzy', 'label_risiko']], use_container_width=True)
            else: st.info("Belum ada data pemeriksaan.")
