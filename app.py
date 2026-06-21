from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import altair as alt
import json
from database import *
from fuzzy_logic import *

app = Flask(__name__)
app.secret_key = "kunci_rahasia_stunting_super_aman"

# Pastikan DB terinisialisasi saat server nyala
with app.app_context():
    inisialisasi_database()

def gaya_tampilan_risiko(skor):
    if skor < 30:  return "✅ Risiko RENDAH"
    if skor < 55:  return "⚠️ Risiko SEDANG"
    if skor < 78:  return "🔴 Risiko TINGGI"
    return            "🚨 Risiko SANGAT TINGGI"

def daftar_rekomendasi(skor, persentase_tinggi, persentase_berat):
    saran = []
    if persentase_tinggi < 90: saran.append("Konsultasi ke Puskesmas/Posyandu untuk pemantauan pertumbuhan tinggi anak secara rutin.")
    if persentase_berat < 80: saran.append("Tingkatkan asupan gizi – berikan MPASI berkualitas tinggi (kaya protein hewani, zat besi, dan zinc).")
    if skor >= 55: saran.append("Anak terindikasi kuat stunting – segera rujuk ke tenaga gizi atau dokter spesialis anak.")
    if skor >= 78: saran.append("Kondisi SANGAT KRITIS! Periksakan kondisi menyeluruh segera dan laporkan ke program gizi nasional.")
    if skor < 30: saran.append("Pertumbuhan sangat baik – pertahankan pola asuh dan makan bergizi seimbang!")
    saran.append("Tetap berikan imunisasi dasar lengkap sesuai jadwal dan selalu jaga kebersihan/sanitasi lingkungan.")
    return saran

@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = verifikasi_login(username, password)
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Coba tambah pengguna (role default: pengguna)
        berhasil = tambah_pengguna(username, password)
        if berhasil:
            flash('Registrasi berhasil! Silakan login menggunakan akun baru Anda.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username sudah digunakan atau terjadi kesalahan.', 'error')
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah keluar dari sistem.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if session.get('role') == 'admin':
        # Admin Dashboard: Hanya statistik (tanpa tabel langsung)
        riwayat = dapatkan_semua_riwayat()
        stats = {
            "total": len(riwayat),
            "tinggi": sum(1 for r in riwayat if 'TINGGI' in r['label_risiko']),
            "rendah": sum(1 for r in riwayat if 'RENDAH' in r['label_risiko'] or 'NORMAL' in r['label_risiko'])
        }
        return render_template('admin.html', stats=stats)
    else:
        # Kader Dashboard: Hanya menu (tanpa tabel langsung)
        return render_template('kader.html')

@app.route('/riwayat')
def riwayat():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if session.get('role') == 'admin':
        data_riwayat = dapatkan_semua_riwayat()
    else:
        data_riwayat = dapatkan_riwayat_berdasarkan_pengguna(session['user_id'])
        
    return render_template('riwayat.html', riwayat=data_riwayat)

@app.route('/tambah_pasien', methods=['POST'])
def tambah_pasien_route():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    nama = request.form['nama']
    jk = request.form['jk']
    tgl_lahir = request.form['tgl_lahir']
    nama_ortu = request.form['nama_ortu']
    
    tambah_pasien(nama, jk, tgl_lahir, nama_ortu, session['user_id'])
    flash(f"Pasien {nama} berhasil didaftarkan!", "success")
    return redirect(url_for('dashboard'))

@app.route('/deteksi', methods=['GET', 'POST'])
def deteksi():
    if not session.get('logged_in') or session.get('role') != 'pengguna':
        return redirect(url_for('login'))
        
    if session.get('role') == 'admin':
        pasien_list = dapatkan_semua_pasien()
    else:
        pasien_list = dapatkan_pasien_berdasarkan_pengguna(session['user_id'])
    
    if request.method == 'GET':
        return render_template('deteksi.html', pasien=pasien_list, hasil=None)
        
    if request.method == 'POST':
        id_pasien = int(request.form['id_pasien'])
        usia = int(request.form['usia'])
        tinggi = float(request.form['tinggi'])
        berat = float(request.form['berat'])
        
        # Cari detail pasien
        data_pasien = next((p for p in pasien_list if p['id'] == id_pasien), None)
        if not data_pasien:
            flash("Pasien tidak ditemukan!", "error")
            return redirect(url_for('deteksi'))
            
        # Hitung Fuzzy
        standar_who = hitung_median_who(usia, data_pasien['jenis_kelamin'])
        persentase_tinggi = (tinggi / standar_who["tinggi"]) * 100
        persentase_berat = (berat / standar_who["berat"]) * 100
        
        derajat_tinggi = fuzzifikasi_tinggi_badan(persentase_tinggi)
        derajat_berat = fuzzifikasi_berat_badan(persentase_berat)
        
        skor_akhir, histori_aturan, kordinat_x, kordinat_y, agregasi = proses_inferensi_mamdani(derajat_tinggi, derajat_berat)
        label_risiko_full = gaya_tampilan_risiko(skor_akhir)
        label_bersih = label_risiko_full.split("Risiko ")[-1]
        
        # Filter aturan yang aktif saja
        aturan_aktif = [r for r in histori_aturan if r['aktif']]
        
        # Simpan riwayat
        simpan_riwayat(id_pasien, usia, tinggi, berat, skor_akhir, label_bersih, session['user_id'])
        
        # Buat Grafik Altair
        tabel_grafik = pd.DataFrame({'Skor Risiko': kordinat_x, 'Derajat Area': kordinat_y})
        grafik_area = alt.Chart(tabel_grafik).mark_area(opacity=0.6, color='#0284c7').encode(
            x=alt.X('Skor Risiko', scale=alt.Scale(domain=[0, 100]), title='Skor Keparahan Stunting'),
            y=alt.Y('Derajat Area', scale=alt.Scale(domain=[0, 1]), title='Derajat Keanggotaan')
        )
        if skor_akhir > 0:
            garis_centroid = alt.Chart(pd.DataFrame({'Skor Risiko': [skor_akhir]})).mark_rule(color='#f43f5e', strokeWidth=3).encode(x='Skor Risiko')
            chart = grafik_area + garis_centroid
        else:
            chart = grafik_area
            
        # Chart configuration for light theme
        chart = chart.properties(width='container', height=300).configure_view(strokeOpacity=0).configure_axis(
            labelColor='#475569', titleColor='#334155', gridColor='#e2e8f0', domainColor='#cbd5e1'
        )
        
        chart_json = chart.to_json()
        
        # Ambil rekomendasi medis
        rekomendasi_list = daftar_rekomendasi(skor_akhir, persentase_tinggi, persentase_berat)
        
        hasil_data = {
            "pasien": data_pasien,
            "usia": usia,
            "tinggi": tinggi,
            "berat": berat,
            "skor": skor_akhir,
            "label": label_risiko_full,
            "rekomendasi": rekomendasi_list,
            "aturan_aktif": aturan_aktif,
            "agregasi": agregasi
        }
        
        flash("Analisis selesai dan riwayat telah disimpan.", "success")
        return render_template('deteksi.html', pasien=pasien_list, hasil=hasil_data, chart_json=chart_json)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
