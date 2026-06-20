import mysql.connector

def run_migration():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_stunting"
        )
        cursor = conn.cursor()
        
        # Coba tambah kolom id_pengguna
        try:
            cursor.execute("ALTER TABLE pasien ADD COLUMN id_pengguna INT DEFAULT 1")
            print("Berhasil menambahkan kolom id_pengguna ke tabel pasien.")
            
            # Tambahkan Foreign Key
            cursor.execute("ALTER TABLE pasien ADD FOREIGN KEY (id_pengguna) REFERENCES users(id)")
            print("Berhasil menambahkan foreign key id_pengguna.")
        except mysql.connector.Error as err:
            print(f"Error (mungkin kolom sudah ada): {err}")
            
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Koneksi gagal: {e}")

if __name__ == '__main__':
    run_migration()
