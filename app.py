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
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Berhasil login!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'error')
            
    return render_template('login.html')

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
        riwayat = dapatkan_semua_riwayat()
        stats = {
            'total': len(riwayat),
            'tinggi': sum(1 for r in riwayat if 'TINGGI' in r['label_risiko']),
            'rendah': sum(1 for r in riwayat if 'RENDAH' in r['label_risiko'])
        }
        return render_template('admin.html', riwayat=riwayat, stats=stats)
    else:
        # Kader Dashboard
        riwayat = dapatkan_semua_riwayat()
        return render_template('kader.html', riwayat=riwayat)

@app.route('/tambah_pasien', methods=['POST'])
def tambah_pasien_route():
    if not session.get('logged_in') or session.get('role') != 'pengguna':
        return redirect(url_for('login'))
        
    nama = request.form['nama']
    jk = request.form['jk']
    tgl_lahir = request.form['tgl_lahir']
    nama_ortu = request.form['nama_ortu']
    
    tambah_pasien(nama, jk, tgl_lahir, nama_ortu)
    flash(f"Pasien {nama} berhasil didaftarkan!", "success")
    return redirect(url_for('dashboard'))

@app.route('/deteksi', methods=['GET', 'POST'])
def deteksi():
    if not session.get('logged_in') or session.get('role') != 'pengguna':
        return redirect(url_for('login'))
        
    pasien_list = dapatkan_semua_pasien()
    
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
        
        skor_akhir, _, kordinat_x, kordinat_y, _ = proses_inferensi_mamdani(derajat_tinggi, derajat_berat)
        label_risiko_full = gaya_tampilan_risiko(skor_akhir)
        label_bersih = label_risiko_full.split("Risiko ")[-1]
        
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
            
        # Chart configuration for dark theme
        chart = chart.properties(width='container', height=300).configure_view(strokeOpacity=0).configure_axis(
            labelColor='#94a3b8', titleColor='#94a3b8', gridColor='#334155', domainColor='#475569'
        )
        
        chart_json = chart.to_json()
        
        hasil_data = {
            "pasien": data_pasien,
            "usia": usia,
            "tinggi": tinggi,
            "berat": berat,
            "skor": skor_akhir,
            "label": label_risiko_full
        }
        
        flash("Analisis selesai dan riwayat telah disimpan.", "success")
        return render_template('deteksi.html', pasien=pasien_list, hasil=hasil_data, chart_json=chart_json)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
