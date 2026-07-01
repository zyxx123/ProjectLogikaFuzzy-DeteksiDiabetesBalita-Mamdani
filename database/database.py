import mysql.connector
from datetime import datetime
import streamlit as st

def buat_koneksi_awal():
    """Koneksi awal untuk memastikan database db_stunting ada"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        return conn
    except Exception as e:
        st.error(f"Gagal koneksi ke MySQL: {e}")
        return None

def buat_koneksi():
    """Koneksi ke database db_stunting"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_stunting"
        )
        return conn
    except Exception as e:
        return None

def inisialisasi_database():
    """Membuat database dan tabel jika belum ada"""
    conn_awal = buat_koneksi_awal()
    if conn_awal is None:
        return False
        
    cursor = conn_awal.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS db_stunting")
    conn_awal.commit()
    cursor.close()
    conn_awal.close()

    conn = buat_koneksi()
    if conn is None:
        return False
        
    cursor = conn.cursor()
    
    # Buat tabel users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('admin', 'pengguna') NOT NULL
        )
    ''')
    
    # Buat tabel pasien
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pasien (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama_anak VARCHAR(100) NOT NULL,
            jenis_kelamin ENUM('Laki-laki', 'Perempuan') NOT NULL,
            tanggal_lahir DATE NOT NULL,
            nama_orang_tua VARCHAR(100) NOT NULL,
            id_pengguna INT DEFAULT 1,
            FOREIGN KEY (id_pengguna) REFERENCES users(id)
        )
    ''')
    
    # Buat tabel riwayat deteksi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS riwayat_deteksi (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_pasien INT NOT NULL,
            tanggal_periksa DATE NOT NULL,
            usia_bulan INT NOT NULL,
            tinggi_cm FLOAT NOT NULL,
            berat_kg FLOAT NOT NULL,
            skor_fuzzy FLOAT NOT NULL,
            label_risiko VARCHAR(50) NOT NULL,
            id_pengguna INT NOT NULL,
            FOREIGN KEY (id_pasien) REFERENCES pasien(id),
            FOREIGN KEY (id_pengguna) REFERENCES users(id)
        )
    ''')
    
    # Insert default users jika tabel kosong
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", ('admin', 'admin123', 'admin'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", ('kader', 'kader123', 'pengguna'))
        
    conn.commit()
    cursor.close()
    conn.close()
    return True

# --- FUNGSI LOGIN ---
def verifikasi_login(username, password):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def tambah_pengguna(username, password, role='pengguna'):
    conn = buat_koneksi()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        return False

def dapatkan_semua_pengguna():
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users ORDER BY id DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def dapatkan_pengguna_by_id(id_user):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (id_user,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def update_pengguna(id_user, username, role, password=None):
    conn = buat_koneksi()
    if not conn: return False
    try:
        cursor = conn.cursor()
        if password:
            cursor.execute("UPDATE users SET username=%s, password=%s, role=%s WHERE id=%s", (username, password, role, id_user))
        else:
            cursor.execute("UPDATE users SET username=%s, role=%s WHERE id=%s", (username, role, id_user))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error update pengguna: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def hapus_pengguna(id_user):
    conn = buat_koneksi()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # 1. Delete riwayat deteksi associated with this user's patients or created by this user
        cursor.execute("DELETE FROM riwayat_deteksi WHERE id_pengguna=%s OR id_pasien IN (SELECT id FROM pasien WHERE id_pengguna=%s)", (id_user, id_user))
        # 2. Delete patients registered by this user
        cursor.execute("DELETE FROM pasien WHERE id_pengguna=%s", (id_user,))
        # 3. Finally delete the user
        cursor.execute("DELETE FROM users WHERE id=%s", (id_user,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error hapus pengguna: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- FUNGSI PASIEN ---
def tambah_pasien(nama, jk, tgl_lahir, nama_ortu, id_pengguna):
    conn = buat_koneksi()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pasien (nama_anak, jenis_kelamin, tanggal_lahir, nama_orang_tua, id_pengguna)
        VALUES (%s, %s, %s, %s, %s)
    ''', (nama, jk, tgl_lahir, nama_ortu, id_pengguna))
    conn.commit()
    cursor.close()
    conn.close()

def dapatkan_semua_pasien():
    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pasien ORDER BY id DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def dapatkan_pasien_berdasarkan_pengguna(id_pengguna):
    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pasien WHERE id_pengguna = %s ORDER BY id DESC", (id_pengguna,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# ==========================
# FUNGSI EDIT & HAPUS PASIEN
# ==========================

def dapatkan_pasien_by_id(id_pasien):
    conn = buat_koneksi()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM pasien WHERE id = %s",
        (id_pasien,)
    )

    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return data


def update_pasien(id_pasien, nama, jk, tgl_lahir, nama_ortu):
    conn = buat_koneksi()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE pasien
            SET nama_anak=%s,
                jenis_kelamin=%s,
                tanggal_lahir=%s,
                nama_orang_tua=%s
            WHERE id=%s
        """, (nama, jk, tgl_lahir, nama_ortu, id_pasien))

        conn.commit()
        return True

    except Exception as e:
        print(f"Error update pasien: {e}")
        return False

    finally:
        cursor.close()
        conn.close()


def hapus_pasien(id_pasien):
    conn = buat_koneksi()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM riwayat_deteksi WHERE id_pasien=%s",
            (id_pasien,)
        )

        cursor.execute(
            "DELETE FROM pasien WHERE id=%s",
            (id_pasien,)
        )

        conn.commit()
        return True

    except Exception as e:
        print(f"Error hapus pasien: {e}")
        return False

    finally:
        cursor.close()
        conn.close()

# --- FUNGSI RIWAYAT DETEKSI ---
def simpan_riwayat(id_pasien, usia_bulan, tinggi, berat, skor, label, id_pengguna):
    conn = buat_koneksi()
    cursor = conn.cursor()
    tgl_sekarang = datetime.now().date()
    cursor.execute('''
        INSERT INTO riwayat_deteksi 
        (id_pasien, tanggal_periksa, usia_bulan, tinggi_cm, berat_kg, skor_fuzzy, label_risiko, id_pengguna)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (id_pasien, tgl_sekarang, usia_bulan, tinggi, berat, skor, label, id_pengguna))
    conn.commit()
    cursor.close()
    conn.close()

def dapatkan_semua_riwayat():
    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.*, p.nama_anak, p.jenis_kelamin, u.username as nama_petugas
        FROM riwayat_deteksi r
        JOIN pasien p ON r.id_pasien = p.id
        JOIN users u ON r.id_pengguna = u.id
        ORDER BY r.tanggal_periksa DESC, r.id DESC
    ''')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def dapatkan_riwayat_berdasarkan_pengguna(id_pengguna):
    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.*, p.nama_anak, p.jenis_kelamin, u.username as nama_petugas
        FROM riwayat_deteksi r
        JOIN pasien p ON r.id_pasien = p.id
        JOIN users u ON r.id_pengguna = u.id
        WHERE r.id_pengguna = %s
        ORDER BY r.tanggal_periksa DESC, r.id DESC
    ''', (id_pengguna,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def dapatkan_riwayat_pasien(id_pasien):
    conn = buat_koneksi()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT * FROM riwayat_deteksi 
        WHERE id_pasien = %s 
        ORDER BY tanggal_periksa DESC
    ''', (id_pasien,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def hapus_riwayat(id_riwayat):
    conn = buat_koneksi()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM riwayat_deteksi WHERE id=%s",
            (id_riwayat,)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error hapus riwayat: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
