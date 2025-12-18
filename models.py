from datetime import datetime
from database import db

class Pasien:
    """Model untuk tabel pasien"""

    def __init__(self, nomor_rm=None, nama_lengkap=None, nik=None, tanggal_lahir=None,
                 jenis_kelamin=None, alamat=None, nomor_telepon=None, ihs_number=None, id=None):
        self.id = id
        self.nomor_rm = nomor_rm
        self.nama_lengkap = nama_lengkap
        self.nik = nik
        self.tanggal_lahir = tanggal_lahir
        self.jenis_kelamin = jenis_kelamin
        self.alamat = alamat
        self.nomor_telepon = nomor_telepon
        self.ihs_number = ihs_number

    def save(self):
        """Menyimpan data pasien baru"""
        query = """
        INSERT INTO pasien (nomor_rm, nama_lengkap, nik, tanggal_lahir, jenis_kelamin, alamat, nomor_telepon, ihs_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.nomor_rm, self.nama_lengkap, self.nik, self.tanggal_lahir,
                 self.jenis_kelamin, self.alamat, self.nomor_telepon, self.ihs_number)
        return db.execute_query(query, params)

    @staticmethod
    def get_all():
        """Mengambil semua data pasien"""
        query = "SELECT * FROM pasien ORDER BY nama_lengkap"
        return db.fetch_query(query)

    @staticmethod
    def get_by_id(id):
        """Mengambil data pasien berdasarkan ID"""
        query = "SELECT * FROM pasien WHERE id = %s"
        result = db.fetch_query(query, (id,))
        return result[0] if result else None

    @staticmethod
    def get_by_nomor_rm(nomor_rm):
        """Mengambil data pasien berdasarkan nomor RM"""
        query = "SELECT * FROM pasien WHERE nomor_rm = %s"
        result = db.fetch_query(query, (nomor_rm,))
        return result[0] if result else None

    def update(self, id):
        """Mengupdate data pasien"""
        query = """
        UPDATE pasien
        SET nama_lengkap = %s, tanggal_lahir = %s, jenis_kelamin = %s,
            alamat = %s, nomor_telepon = %s
        WHERE id = %s
        """
        params = (self.nama_lengkap, self.tanggal_lahir, self.jenis_kelamin,
                 self.alamat, self.nomor_telepon, id)
        return db.execute_query(query, params)

    def update(self, id):
        """Mengupdate data pasien"""
        query = """
        UPDATE pasien
        SET nama_lengkap = %s, nik = %s, tanggal_lahir = %s, jenis_kelamin = %s,
            alamat = %s, nomor_telepon = %s
        WHERE id = %s
        """
        params = (self.nama_lengkap, self.nik, self.tanggal_lahir, self.jenis_kelamin,
                 self.alamat, self.nomor_telepon, id)
        return db.execute_query(query, params)

    def update_ihs(self, id, ihs_number):
        """Update IHS number dan sync timestamp"""
        query = """
        UPDATE pasien
        SET ihs_number = %s, sync_ihs_at = NOW()
        WHERE id = %s
        """
        return db.execute_query(query, (ihs_number, id))

    @staticmethod
    def delete(id):
        """Menghapus data pasien"""
        query = "DELETE FROM pasien WHERE id = %s"
        return db.execute_query(query, (id,))

    @staticmethod
    def get_patients_without_ihs():
        """Mengambil pasien yang belum memiliki IHS number"""
        query = """
        SELECT * FROM pasien
        WHERE ihs_number IS NULL AND nik IS NOT NULL AND nik != ''
        ORDER BY created_at DESC
        """
        return db.fetch_query(query)

    @staticmethod
    def get_patients_with_nik():
        """Mengambil semua pasien yang memiliki NIK"""
        query = """
        SELECT * FROM pasien
        WHERE nik IS NOT NULL AND nik != ''
        ORDER BY nama_lengkap
        """
        return db.fetch_query(query)


class Dokter:
    """Model untuk tabel dokter"""

    def __init__(self, nomor_sip=None, nama_dokter=None, spesialisasi=None,
                 nomor_telepon=None, id=None):
        self.id = id
        self.nomor_sip = nomor_sip
        self.nama_dokter = nama_dokter
        self.spesialisasi = spesialisasi
        self.nomor_telepon = nomor_telepon

    def save(self):
        """Menyimpan data dokter baru"""
        query = """
        INSERT INTO dokter (nomor_sip, nama_dokter, spesialisasi, nomor_telepon)
        VALUES (%s, %s, %s, %s)
        """
        params = (self.nomor_sip, self.nama_dokter, self.spesialisasi, self.nomor_telepon)
        return db.execute_query(query, params)

    @staticmethod
    def get_all():
        """Mengambil semua data dokter"""
        query = "SELECT * FROM dokter ORDER BY nama_dokter"
        return db.fetch_query(query)

    @staticmethod
    def get_by_id(id):
        """Mengambil data dokter berdasarkan ID"""
        query = "SELECT * FROM dokter WHERE id = %s"
        result = db.fetch_query(query, (id,))
        return result[0] if result else None

    def update(self, id):
        """Mengupdate data dokter"""
        query = """
        UPDATE dokter
        SET nama_dokter = %s, spesialisasi = %s, nomor_telepon = %s
        WHERE id = %s
        """
        params = (self.nama_dokter, self.spesialisasi, self.nomor_telepon, id)
        return db.execute_query(query, params)

    @staticmethod
    def delete(id):
        """Menghapus data dokter"""
        query = "DELETE FROM dokter WHERE id = %s"
        return db.execute_query(query, (id,))


class Poliklinik:
    """Model untuk tabel poliklinik"""

    def __init__(self, nama_poli=None, gedung=None, lantai=None, id=None):
        self.id = id
        self.nama_poli = nama_poli
        self.gedung = gedung
        self.lantai = lantai

    def save(self):
        """Menyimpan data poliklinik baru"""
        query = """
        INSERT INTO poliklinik (nama_poli, gedung, lantai)
        VALUES (%s, %s, %s)
        """
        params = (self.nama_poli, self.gedung, self.lantai)
        return db.execute_query(query, params)

    @staticmethod
    def get_all():
        """Mengambil semua data poliklinik"""
        query = "SELECT * FROM poliklinik ORDER BY nama_poli"
        return db.fetch_query(query)

    @staticmethod
    def get_by_id(id):
        """Mengambil data poliklinik berdasarkan ID"""
        query = "SELECT * FROM poliklinik WHERE id = %s"
        result = db.fetch_query(query, (id,))
        return result[0] if result else None

    def update(self, id):
        """Mengupdate data poliklinik"""
        query = """
        UPDATE poliklinik
        SET nama_poli = %s, gedung = %s, lantai = %s
        WHERE id = %s
        """
        params = (self.nama_poli, self.gedung, self.lantai, id)
        return db.execute_query(query, params)

    @staticmethod
    def delete(id):
        """Menghapus data poliklinik"""
        query = "DELETE FROM poliklinik WHERE id = %s"
        return db.execute_query(query, (id,))


class Antrian:
    """Model untuk tabel antrian"""

    def __init__(self, nomor_antrian=None, id_pasien=None, id_dokter=None,
                 id_poliklinik=None, tanggal_kunjungan=None, keluhan=None,
                 status='menunggu', id=None):
        self.id = id
        self.nomor_antrian = nomor_antrian
        self.id_pasien = id_pasien
        self.id_dokter = id_dokter
        self.id_poliklinik = id_poliklinik
        self.tanggal_kunjungan = tanggal_kunjungan or datetime.now().date()
        self.keluhan = keluhan
        self.status = status

    def save(self):
        """Menyimpan data antrian baru"""
        query = """
        INSERT INTO antrian (nomor_antrian, id_pasien, id_dokter, id_poliklinik,
                           tanggal_kunjungan, keluhan, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.nomor_antrian, self.id_pasien, self.id_dokter,
                 self.id_poliklinik, self.tanggal_kunjungan, self.keluhan, self.status)
        return db.execute_query(query, params)

    @staticmethod
    def get_all():
        """Mengambil semua data antrian dengan join ke tabel lain"""
        query = """
        SELECT a.*, p.nama_lengkap, d.nama_dokter, pol.nama_poli
        FROM antrian a
        JOIN pasien p ON a.id_pasien = p.id
        JOIN dokter d ON a.id_dokter = d.id
        JOIN poliklinik pol ON a.id_poliklinik = pol.id
        ORDER BY a.tanggal_kunjungan, a.nomor_antrian
        """
        return db.fetch_query(query)

    @staticmethod
    def get_today_queue():
        """Mengambil data antrian hari ini"""
        query = """
        SELECT a.*, p.nama_lengkap, d.nama_dokter, pol.nama_poli
        FROM antrian a
        JOIN pasien p ON a.id_pasien = p.id
        JOIN dokter d ON a.id_dokter = d.id
        JOIN poliklinik pol ON a.id_poliklinik = pol.id
        WHERE a.tanggal_kunjungan = CURDATE()
        ORDER BY a.nomor_antrian
        """
        return db.fetch_query(query)

    @staticmethod
    def get_by_poliklinik(id_poliklinik, tanggal=None):
        """Mengambil antrian berdasarkan poliklinik dan tanggal"""
        if not tanggal:
            tanggal = datetime.now().date()

        query = """
        SELECT a.*, p.nama_lengkap, d.nama_dokter, pol.nama_poli
        FROM antrian a
        JOIN pasien p ON a.id_pasien = p.id
        JOIN dokter d ON a.id_dokter = d.id
        JOIN poliklinik pol ON a.id_poliklinik = pol.id
        WHERE a.id_poliklinik = %s AND a.tanggal_kunjungan = %s
        ORDER BY a.nomor_antrian
        """
        return db.fetch_query(query, (id_poliklinik, tanggal))

    def update_status(self, id, status):
        """Mengupdate status antrian"""
        query = "UPDATE antrian SET status = %s WHERE id = %s"
        return db.execute_query(query, (status, id))

    @staticmethod
    def get_next_queue_number(id_poliklinik, tanggal=None):
        """Mengambil nomor antrian selanjutnya untuk poliklinik tertentu"""
        if not tanggal:
            tanggal = datetime.now().date()

        query = """
        SELECT COALESCE(MAX(nomor_antrian), 0) + 1 as next_number
        FROM antrian
        WHERE id_poliklinik = %s AND tanggal_kunjungan = %s
        """
        result = db.fetch_query(query, (id_poliklinik, tanggal))
        return result[0]['next_number'] if result else 1

    @staticmethod
    def delete(id):
        """Menghapus data antrian"""
        query = "DELETE FROM antrian WHERE id = %s"
        return db.execute_query(query, (id,))