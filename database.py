import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', 3306)
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'simrs')

    def connect(self):
        """Membuat koneksi ke database MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("✅ Berhasil terkoneksi ke database MySQL")
                return True
        except Error as e:
            print(f"❌ Gagal terkoneksi ke database: {e}")
            return False

    def disconnect(self):
        """Menutup koneksi database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Koneksi database ditutup")

    def execute_query(self, query, params=None):
        """Menjalankan query INSERT, UPDATE, DELETE"""
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            print(f"✅ Query berhasil dieksekusi: {cursor.rowcount} baris terpengaruh")
            return cursor.lastrowid if query.strip().upper().startswith('INSERT') else cursor.rowcount
        except Error as e:
            print(f"❌ Error saat mengeksekusi query: {e}")
            self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()

    def fetch_query(self, query, params=None):
        """Menjalankan query SELECT dan mengembalikan hasilnya"""
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            print(f"✅ Query berhasil, ditemukan {len(result)} baris")
            return result
        except Error as e:
            print(f"❌ Error saat mengambil data: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def create_database_and_tables(self):
        """Membuat database dan tabel jika belum ada"""
        try:
            # Koneksi tanpa database dulu
            temp_connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            cursor = temp_connection.cursor()

            # Buat database jika belum ada
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"✅ Database '{self.database}' siap digunakan")

            cursor.close()
            temp_connection.close()

            # Sekarang koneksi ke database yang sudah dibuat
            self.connect()

            # Buat tabel-tabel
            self._create_tables()

        except Error as e:
            print(f"❌ Error saat membuat database: {e}")
            return False

    def _create_tables(self):
        """Membuat tabel-tabel yang diperlukan"""

        # Tabel pasien
        create_pasien_table = """
        CREATE TABLE IF NOT EXISTS pasien (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nomor_rm VARCHAR(20) UNIQUE NOT NULL,
            nama_lengkap VARCHAR(100) NOT NULL,
            nik VARCHAR(16),
            tanggal_lahir DATE,
            jenis_kelamin ENUM('L', 'P'),
            alamat TEXT,
            nomor_telepon VARCHAR(15),
            ihs_number VARCHAR(100),
            sync_ihs_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Tabel dokter
        create_dokter_table = """
        CREATE TABLE IF NOT EXISTS dokter (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nomor_sip VARCHAR(30) UNIQUE NOT NULL,
            nama_dokter VARCHAR(100) NOT NULL,
            spesialisasi VARCHAR(50),
            nomor_telepon VARCHAR(15),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Tabel poliklinik
        create_poliklinik_table = """
        CREATE TABLE IF NOT EXISTS poliklinik (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama_poli VARCHAR(50) UNIQUE NOT NULL,
            gedung VARCHAR(20),
            lantai INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Tabel antrian
        create_antrian_table = """
        CREATE TABLE IF NOT EXISTS antrian (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nomor_antrian INT NOT NULL,
            id_pasien INT,
            id_dokter INT,
            id_poliklinik INT,
            tanggal_kunjungan DATE,
            keluhan TEXT,
            status ENUM('menunggu', 'dilayani', 'selesai') DEFAULT 'menunggu',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_pasien) REFERENCES pasien(id),
            FOREIGN KEY (id_dokter) REFERENCES dokter(id),
            FOREIGN KEY (id_poliklinik) REFERENCES poliklinik(id)
        )
        """

        tables = [
            create_pasien_table,
            create_dokter_table,
            create_poliklinik_table,
            create_antrian_table
        ]

        for table_query in tables:
            self.execute_query(table_query)

        print("✅ Semua tabel berhasil dibuat")

# Singleton instance
db = DatabaseConnection()