from tabulate import tabulate
from models import Pasien, Dokter, Poliklinik, Antrian
from datetime import datetime

class CRUDOperations:
    """Class untuk menangani operasi CRUD pada setiap model"""

    # ================= PASIEN OPERATIONS =================
    @staticmethod
    def pasien_menu():
        """Menu untuk operasi pasien"""
        while True:
            print("\n" + "="*50)
            print("         MENU MANAJEMEN PASIEN")
            print("="*50)
            print("1. Tambah Pasien Baru")
            print("2. Lihat Semua Pasien")
            print("3. Cari Pasien")
            print("4. Update Data Pasien")
            print("5. Hapus Data Pasien")
            print("0. Kembali ke Menu Utama")

            choice = input("\nPilih menu [0-5]: ")

            if choice == '1':
                CRUDOperations.tambah_pasien()
            elif choice == '2':
                CRUDOperations.lihat_semua_pasien()
            elif choice == '3':
                CRUDOperations.cari_pasien()
            elif choice == '4':
                CRUDOperations.update_pasien()
            elif choice == '5':
                CRUDOperations.hapus_pasien()
            elif choice == '0':
                break
            else:
                print("\n❌ Pilihan tidak valid. Silakan coba lagi.")

    @staticmethod
    def tambah_pasien():
        """Menambah pasien baru"""
        print("\n--- TAMBAH PASIEN BARU ---")

        try:
            nomor_rm = input("Nomor Rekam Medis: ")

            # Cek apakah nomor RM sudah ada
            if Pasien.get_by_nomor_rm(nomor_rm):
                print(f"\n❌ Nomor RM {nomor_rm} sudah terdaftar!")
                return

            nama_lengkap = input("Nama Lengkap: ")
            nik = input("NIK (16 digit, opsional): ")
            tanggal_lahir = input("Tanggal Lahir (YYYY-MM-DD): ")
            jenis_kelamin = input("Jenis Kelamin (L/P): ").upper()
            alamat = input("Alamat: ")
            nomor_telepon = input("Nomor Telepon: ")

            pasien = Pasien(
                nomor_rm=nomor_rm,
                nama_lengkap=nama_lengkap,
                nik=nik if nik else None,
                tanggal_lahir=tanggal_lahir,
                jenis_kelamin=jenis_kelamin,
                alamat=alamat,
                nomor_telepon=nomor_telepon
            )

            if pasien.save():
                print(f"\n✅ Pasien {nama_lengkap} berhasil ditambahkan!")
            else:
                print("\n❌ Gagal menambahkan pasien!")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    @staticmethod
    def lihat_semua_pasien():
        """Menampilkan semua pasien"""
        print("\n--- DAFTAR SEMUA PASIEN ---")

        pasiens = Pasien.get_all()

        if not pasiens:
            print("\n📭 Belum ada data pasien.")
            return

        # Format data untuk tabulasi
        headers = ['ID', 'No. RM', 'Nama Lengkap', 'Tanggal Lahir', 'Jenis Kelamin', 'Telepon']
        rows = []

        for pasien in pasiens:
            rows.append([
                pasien['id'],
                pasien['nomor_rm'],
                pasien['nama_lengkap'],
                pasien['tanggal_lahir'],
                pasien['jenis_kelamin'],
                pasien['nomor_telepon'] or '-'
            ])

        print("\n" + tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\nTotal: {len(pasiens)} pasien")

    @staticmethod
    def cari_pasien():
        """Mencari pasien berdasarkan nama atau nomor RM"""
        print("\n--- CARI PASIEN ---")
        keyword = input("Masukkan nama atau nomor RM: ")

        # Cari berdasarkan nomor RM
        pasien = Pasien.get_by_nomor_rm(keyword)
        if pasien:
            headers = ['ID', 'No. RM', 'Nama Lengkap', 'Tanggal Lahir', 'Jenis Kelamin', 'Alamat', 'Telepon']
            rows = [[
                pasien['id'],
                pasien['nomor_rm'],
                pasien['nama_lengkap'],
                pasien['tanggal_lahir'],
                pasien['jenis_kelamin'],
                pasien['alamat'] or '-',
                pasien['nomor_telepon'] or '-'
            ]]
            print("\n" + tabulate(rows, headers=headers, tablefmt='grid'))
            return pasien

        # Jika tidak ketemu, beri pesan
        print(f"\n❌ Pasien dengan nama atau RM '{keyword}' tidak ditemukan!")
        return None

    @staticmethod
    def update_pasien():
        """Update data pasien"""
        print("\n--- UPDATE DATA PASIEN ---")

        # Cari pasien dulu
        pasien = CRUDOperations.cari_pasien()
        if not pasien:
            return

        print("\nMasukkan data baru (kosongkan jika tidak ingin mengubah):")

        nama_lengkap = input(f"Nama Lengkap [{pasien['nama_lengkap']}]: ") or pasien['nama_lengkap']
        tanggal_lahir = input(f"Tanggal Lahir [{pasien['tanggal_lahir']}]: ") or pasien['tanggal_lahir']
        jenis_kelamin = input(f"Jenis Kelamin (L/P) [{pasien['jenis_kelamin']}]: ").upper() or pasien['jenis_kelamin']
        alamat = input(f"Alamat [{pasien['alamat'] or '-'}]: ") or pasien['alamat']
        nomor_telepon = input(f"Nomor Telepon [{pasien['nomor_telepon'] or '-'}]: ") or pasien['nomor_telepon']

        # Buat objek pasien baru
        pasien_update = Pasien(
            nama_lengkap=nama_lengkap,
            tanggal_lahir=tanggal_lahir,
            jenis_kelamin=jenis_kelamin,
            alamat=alamat,
            nomor_telepon=nomor_telepon
        )

        if pasien_update.update(pasien['id']):
            print(f"\n✅ Data pasien {nama_lengkap} berhasil diupdate!")
        else:
            print("\n❌ Gagal mengupdate data pasien!")

    @staticmethod
    def hapus_pasien():
        """Menghapus data pasien"""
        print("\n--- HAPUS DATA PASIEN ---")

        # Cari pasien dulu
        pasien = CRUDOperations.cari_pasien()
        if not pasien:
            return

        confirm = input(f"\n⚠️  Yakin ingin menghapus pasien {pasien['nama_lengkap']}? (y/N): ")

        if confirm.lower() == 'y':
            if Pasien.delete(pasien['id']):
                print(f"\n✅ Pasien {pasien['nama_lengkap']} berhasil dihapus!")
            else:
                print("\n❌ Gagal menghapus pasien!")
        else:
            print("\n❌ Penghapusan dibatalkan.")

    # ================= DOKTER OPERATIONS =================
    @staticmethod
    def dokter_menu():
        """Menu untuk operasi dokter"""
        while True:
            print("\n" + "="*50)
            print("         MENU MANAJEMEN DOKTER")
            print("="*50)
            print("1. Tambah Dokter Baru")
            print("2. Lihat Semua Dokter")
            print("3. Update Data Dokter")
            print("4. Hapus Data Dokter")
            print("0. Kembali ke Menu Utama")

            choice = input("\nPilih menu [0-4]: ")

            if choice == '1':
                CRUDOperations.tambah_dokter()
            elif choice == '2':
                CRUDOperations.lihat_semua_dokter()
            elif choice == '3':
                CRUDOperations.update_dokter()
            elif choice == '4':
                CRUDOperations.hapus_dokter()
            elif choice == '0':
                break
            else:
                print("\n❌ Pilihan tidak valid. Silakan coba lagi.")

    @staticmethod
    def tambah_dokter():
        """Menambah dokter baru"""
        print("\n--- TAMBAH DOKTER BARU ---")

        try:
            nomor_sip = input("Nomor SIP: ")
            nama_dokter = input("Nama Dokter: ")
            spesialisasi = input("Spesialisasi: ")
            nomor_telepon = input("Nomor Telepon: ")

            dokter = Dokter(
                nomor_sip=nomor_sip,
                nama_dokter=nama_dokter,
                spesialisasi=spesialisasi,
                nomor_telepon=nomor_telepon
            )

            if dokter.save():
                print(f"\n✅ Dokter {nama_dokter} berhasil ditambahkan!")
            else:
                print("\n❌ Gagal menambahkan dokter!")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    @staticmethod
    def lihat_semua_dokter():
        """Menampilkan semua dokter"""
        print("\n--- DAFTAR SEMUA DOKTER ---")

        dokters = Dokter.get_all()

        if not dokters:
            print("\n📭 Belum ada data dokter.")
            return

        headers = ['ID', 'No. SIP', 'Nama Dokter', 'Spesialisasi', 'Telepon']
        rows = []

        for dokter in dokters:
            rows.append([
                dokter['id'],
                dokter['nomor_sip'],
                dokter['nama_dokter'],
                dokter['spesialisasi'] or '-',
                dokter['nomor_telepon'] or '-'
            ])

        print("\n" + tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\nTotal: {len(dokters)} dokter")

    @staticmethod
    def update_dokter():
        """Update data dokter"""
        print("\n--- UPDATE DATA DOKTER ---")

        dokters = Dokter.get_all()
        if not dokters:
            print("\n📭 Belum ada data dokter.")
            return

        # Tampilkan daftar dokter
        print("\nDaftar Dokter:")
        for i, dokter in enumerate(dokters, 1):
            print(f"{i}. {dokter['nama_dokter']} - {dokter['spesialisasi'] or 'Spesialisasi belum ditentukan'}")

        try:
            choice = int(input("\nPilih dokter (nomor): ")) - 1
            if choice < 0 or choice >= len(dokters):
                print("\n❌ Pilihan tidak valid!")
                return

            dokter = dokters[choice]

            print("\nMasukkan data baru (kosongkan jika tidak ingin mengubah):")
            nama_dokter = input(f"Nama Dokter [{dokter['nama_dokter']}]: ") or dokter['nama_dokter']
            spesialisasi = input(f"Spesialisasi [{dokter['spesialisasi'] or '-'}]: ") or dokter['spesialisasi']
            nomor_telepon = input(f"Nomor Telepon [{dokter['nomor_telepon'] or '-'}]: ") or dokter['nomor_telepon']

            dokter_update = Dokter(
                nama_dokter=nama_dokter,
                spesialisasi=spesialisasi,
                nomor_telepon=nomor_telepon
            )

            if dokter_update.update(dokter['id']):
                print(f"\n✅ Data dokter {nama_dokter} berhasil diupdate!")
            else:
                print("\n❌ Gagal mengupdate data dokter!")

        except ValueError:
            print("\n❌ Masukkan angka yang valid!")

    @staticmethod
    def hapus_dokter():
        """Menghapus data dokter"""
        print("\n--- HAPUS DATA DOKTER ---")

        dokters = Dokter.get_all()
        if not dokters:
            print("\n📭 Belum ada data dokter.")
            return

        # Tampilkan daftar dokter
        print("\nDaftar Dokter:")
        for i, dokter in enumerate(dokters, 1):
            print(f"{i}. {dokter['nama_dokter']} - {dokter['spesialisasi'] or 'Spesialisasi belum ditentukan'}")

        try:
            choice = int(input("\nPilih dokter yang akan dihapus (nomor): ")) - 1
            if choice < 0 or choice >= len(dokters):
                print("\n❌ Pilihan tidak valid!")
                return

            dokter = dokters[choice]
            confirm = input(f"\n⚠️  Yakin ingin menghapus dokter {dokter['nama_dokter']}? (y/N): ")

            if confirm.lower() == 'y':
                if Dokter.delete(dokter['id']):
                    print(f"\n✅ Dokter {dokter['nama_dokter']} berhasil dihapus!")
                else:
                    print("\n❌ Gagal menghapus dokter!")
            else:
                print("\n❌ Penghapusan dibatalkan.")

        except ValueError:
            print("\n❌ Masukkan angka yang valid!")

    # ================= POLIKLINIK OPERATIONS =================
    @staticmethod
    def poliklinik_menu():
        """Menu untuk operasi poliklinik"""
        while True:
            print("\n" + "="*50)
            print("        MENU MANAJEMEN POLIKLINIK")
            print("="*50)
            print("1. Tambah Poliklinik Baru")
            print("2. Lihat Semua Poliklinik")
            print("3. Update Data Poliklinik")
            print("4. Hapus Data Poliklinik")
            print("0. Kembali ke Menu Utama")

            choice = input("\nPilih menu [0-4]: ")

            if choice == '1':
                CRUDOperations.tambah_poliklinik()
            elif choice == '2':
                CRUDOperations.lihat_semua_poliklinik()
            elif choice == '3':
                CRUDOperations.update_poliklinik()
            elif choice == '4':
                CRUDOperations.hapus_poliklinik()
            elif choice == '0':
                break
            else:
                print("\n❌ Pilihan tidak valid. Silakan coba lagi.")

    @staticmethod
    def tambah_poliklinik():
        """Menambah poliklinik baru"""
        print("\n--- TAMBAH POLIKLINIK BARU ---")

        try:
            nama_poli = input("Nama Poliklinik: ")
            gedung = input("Gedung: ")
            lantai = input("Lantai: ")

            poliklinik = Poliklinik(
                nama_poli=nama_poli,
                gedung=gedung,
                lantai=int(lantai) if lantai else None
            )

            if poliklinik.save():
                print(f"\n✅ Poliklinik {nama_poli} berhasil ditambahkan!")
            else:
                print("\n❌ Gagal menambahkan poliklinik!")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    @staticmethod
    def lihat_semua_poliklinik():
        """Menampilkan semua poliklinik"""
        print("\n--- DAFTAR SEMUA POLIKLINIK ---")

        polikliniks = Poliklinik.get_all()

        if not polikliniks:
            print("\n📭 Belum ada data poliklinik.")
            return

        headers = ['ID', 'Nama Poliklinik', 'Gedung', 'Lantai']
        rows = []

        for pol in polikliniks:
            rows.append([
                pol['id'],
                pol['nama_poli'],
                pol['gedung'] or '-',
                pol['lantai'] or '-'
            ])

        print("\n" + tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\nTotal: {len(polikliniks)} poliklinik")

    @staticmethod
    def update_poliklinik():
        """Update data poliklinik"""
        print("\n--- UPDATE DATA POLIKLINIK ---")

        polikliniks = Poliklinik.get_all()
        if not polikliniks:
            print("\n📭 Belum ada data poliklinik.")
            return

        print("\nDaftar Poliklinik:")
        for i, pol in enumerate(polikliniks, 1):
            print(f"{i}. {pol['nama_poli']} - Gedung {pol['gedung'] or '-'}, Lantai {pol['lantai'] or '-'}")

        try:
            choice = int(input("\nPilih poliklinik (nomor): ")) - 1
            if choice < 0 or choice >= len(polikliniks):
                print("\n❌ Pilihan tidak valid!")
                return

            pol = polikliniks[choice]

            print("\nMasukkan data baru (kosongkan jika tidak ingin mengubah):")
            nama_poli = input(f"Nama Poliklinik [{pol['nama_poli']}]: ") or pol['nama_poli']
            gedung = input(f"Gedung [{pol['gedung'] or '-'}]: ") or pol['gedung']
            lantai = input(f"Lantai [{pol['lantai'] or '-'}]: ")

            pol_update = Poliklinik(
                nama_poli=nama_poli,
                gedung=gedung,
                lantai=int(lantai) if lantai else pol['lantai']
            )

            if pol_update.update(pol['id']):
                print(f"\n✅ Data poliklinik {nama_poli} berhasil diupdate!")
            else:
                print("\n❌ Gagal mengupdate data poliklinik!")

        except ValueError:
            print("\n❌ Masukkan angka yang valid!")

    @staticmethod
    def hapus_poliklinik():
        """Menghapus data poliklinik"""
        print("\n--- HAPUS DATA POLIKLINIK ---")

        polikliniks = Poliklinik.get_all()
        if not polikliniks:
            print("\n📭 Belum ada data poliklinik.")
            return

        print("\nDaftar Poliklinik:")
        for i, pol in enumerate(polikliniks, 1):
            print(f"{i}. {pol['nama_poli']} - Gedung {pol['gedung'] or '-'}, Lantai {pol['lantai'] or '-'}")

        try:
            choice = int(input("\nPilih poliklinik yang akan dihapus (nomor): ")) - 1
            if choice < 0 or choice >= len(polikliniks):
                print("\n❌ Pilihan tidak valid!")
                return

            pol = polikliniks[choice]
            confirm = input(f"\n⚠️  Yakin ingin menghapus poliklinik {pol['nama_poli']}? (y/N): ")

            if confirm.lower() == 'y':
                if Poliklinik.delete(pol['id']):
                    print(f"\n✅ Poliklinik {pol['nama_poli']} berhasil dihapus!")
                else:
                    print("\n❌ Gagal menghapus poliklinik!")
            else:
                print("\n❌ Penghapusan dibatalkan.")

        except ValueError:
            print("\n❌ Masukkan angka yang valid!")

    # ================= ANTRIAN OPERATIONS =================
    @staticmethod
    def antrian_menu():
        """Menu untuk operasi antrian"""
        while True:
            print("\n" + "="*50)
            print("         MENU MANAJEMEN ANTRIAN")
            print("="*50)
            print("1. Ambil Antrian Baru")
            print("2. Lihat Semua Antrian")
            print("3. Lihat Antrian Hari Ini")
            print("4. Lihat Antrian per Poliklinik")
            print("5. Update Status Antrian")
            print("6. Hapus Antrian")
            print("0. Kembali ke Menu Utama")

            choice = input("\nPilih menu [0-6]: ")

            if choice == '1':
                CRUDOperations.ambil_antrian()
            elif choice == '2':
                CRUDOperations.lihat_semua_antrian()
            elif choice == '3':
                CRUDOperations.lihat_antrian_hari_ini()
            elif choice == '4':
                CRUDOperations.lihat_antrian_per_poli()
            elif choice == '5':
                CRUDOperations.update_status_antrian()
            elif choice == '6':
                CRUDOperations.hapus_antrian()
            elif choice == '0':
                break
            else:
                print("\n❌ Pilihan tidak valid. Silakan coba lagi.")

    @staticmethod
    def ambil_antrian():
        """Mengambil antrian baru"""
        print("\n--- AMBIL ANTRIAN BARU ---")

        try:
            # Pilih pasien
            pasiens = Pasien.get_all()
            if not pasiens:
                print("\n📭 Belum ada data pasien. Silakan tambahkan pasien terlebih dahulu.")
                return

            print("\nDaftar Pasien:")
            for i, pasien in enumerate(pasiens[:10], 1):  # Tampilkan 10 pasien pertama
                print(f"{i}. {pasien['nama_lengkap']} ({pasien['nomor_rm']})")

            if len(pasiens) > 10:
                print("... (dan lainnya)")

            choice_pasien = int(input("\nPilih pasien (nomor): ")) - 1
            if choice_pasien < 0 or choice_pasien >= len(pasiens):
                print("\n❌ Pilihan tidak valid!")
                return

            pasien = pasiens[choice_pasien]

            # Pilih poliklinik
            polikliniks = Poliklinik.get_all()
            if not polikliniks:
                print("\n📭 Belum ada data poliklinik. Silakan tambahkan poliklinik terlebih dahulu.")
                return

            print("\nDaftar Poliklinik:")
            for i, pol in enumerate(polikliniks, 1):
                print(f"{i}. {pol['nama_poli']}")

            choice_poli = int(input("\nPilih poliklinik (nomor): ")) - 1
            if choice_poli < 0 or choice_poli >= len(polikliniks):
                print("\n❌ Pilihan tidak valid!")
                return

            poliklinik = polikliniks[choice_poli]

            # Pilih dokter
            dokters = Dokter.get_all()
            if not dokters:
                print("\n📭 Belum ada data dokter. Silakan tambahkan dokter terlebih dahulu.")
                return

            print("\nDaftar Dokter:")
            for i, dokter in enumerate(dokters, 1):
                print(f"{i}. dr. {dokter['nama_dokter']} - {dokter['spesialisasi'] or 'Spesialisasi belum ditentukan'}")

            choice_dokter = int(input("\nPilih dokter (nomor): ")) - 1
            if choice_dokter < 0 or choice_dokter >= len(dokters):
                print("\n❌ Pilihan tidak valid!")
                return

            dokter = dokters[choice_dokter]

            # Input data antrian
            tanggal = input("Tanggal Kunjungan (YYYY-MM-DD, kosongkan untuk hari ini): ") or datetime.now().date()
            keluhan = input("Keluhan: ")

            # Ambil nomor antrian
            nomor_antrian = Antrian.get_next_queue_number(poliklinik['id'], tanggal)

            # Buat antrian
            antrian = Antrian(
                nomor_antrian=nomor_antrian,
                id_pasien=pasien['id'],
                id_dokter=dokter['id'],
                id_poliklinik=poliklinik['id'],
                tanggal_kunjungan=tanggal,
                keluhan=keluhan
            )

            if antrian.save():
                print(f"\n✅ Antrian berhasil dibuat!")
                print(f"   Nomor Antrian: {nomor_antrian}")
                print(f"   Pasien: {pasien['nama_lengkap']}")
                print(f"   Poliklinik: {poliklinik['nama_poli']}")
                print(f"   Dokter: dr. {dokter['nama_dokter']}")
                print(f"   Tanggal: {tanggal}")
            else:
                print("\n❌ Gagal membuat antrian!")

        except ValueError:
            print("\n❌ Masukkan angka yang valid!")
        except Exception as e:
            print(f"\n❌ Error: {e}")

    @staticmethod
    def lihat_semua_antrian():
        """Menampilkan semua antrian"""
        print("\n--- DAFTAR SEMUA ANTRIAN ---")

        antrians = Antrian.get_all()

        if not antrians:
            print("\n📭 Belum ada data antrian.")
            return

        headers = ['No.', 'RM', 'Pasien', 'Dokter', 'Poliklinik', 'Tanggal', 'No. Antrian', 'Status']
        rows = []

        for i, antrian in enumerate(antrians, 1):
            status_icon = "⏳" if antrian['status'] == 'menunggu' else "👨‍⚕️" if antrian['status'] == 'dilayani' else "✅"
            rows.append([
                i,
                antrian.get('nomor_rm', '-'),
                antrian['nama_lengkap'],
                f"dr. {antrian['nama_dokter']}",
                antrian['nama_poli'],
                antrian['tanggal_kunjungan'],
                antrian['nomor_antrian'],
                f"{status_icon} {antrian['status'].title()}"
            ])

        print("\n" + tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\nTotal: {len(antrians)} antrian")

    @staticmethod
    def lihat_antrian_hari_ini():
        """Menampilkan antrian hari ini"""
        print("\n--- DAFTAR ANTRIAN HARI INI ---")

        antrians = Antrian.get_today_queue()

        if not antrians:
            print("\n📭 Tidak ada antrian hari ini.")
            return

        headers = ['No.', 'No. Antrian', 'Pasien', 'Dokter', 'Poliklinik', 'Status']
        rows = []

        for i, antrian in enumerate(antrians, 1):
            status_icon = "⏳" if antrian['status'] == 'menunggu' else "👨‍⚕️" if antrian['status'] == 'dilayani' else "✅"
            rows.append([
                i,
                antrian['nomor_antrian'],
                antrian['nama_lengkap'],
                f"dr. {antrian['nama_dokter']}",
                antrian['nama_poli'],
                f"{status_icon} {antrian['status'].title()}"
            ])

        print("\n" + tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\nTotal antrian hari ini: {len(antrians)}")

    @staticmethod
    def lihat_antrian_per_poli():
        """Menampilkan antrian per poliklinik"""
        print("\n--- ANTRIAN PER POLIKLINIK ---")

        polikliniks = Poliklinik.get_all()
        if not polikliniks:
            print("\n📭 Belum ada data poliklinik.")
            return

        print("\nDaftar Poliklinik:")
        for i, pol in enumerate(polikliniks, 1):
            print(f"{i}. {pol['nama_poli']}")

        try:
            choice = int(input("\nPilih poliklinik (nomor): ")) - 1
            if choice < 0 or choice >= len(polikliniks):
                print("\n❌ Pilihan tidak valid!")
                return

            pol = polikliniks[choice]
            tanggal = input("Tanggal (YYYY-MM-DD, kosongkan untuk hari ini): ") or datetime.now().date()

            antrians = Antrian.get_by_poliklinik(pol['id'], tanggal)

            if not antrians:
                print(f"\n📭 Tidak ada antrian untuk poliklinik {pol['nama_poli']} pada tanggal {tanggal}.")
                return

            headers = ['No.', 'No. Antrian', 'Pasien', 'Dokter', 'Status']
            rows = []

            for i, antrian in enumerate(antrians, 1):
                status_icon = "⏳" if antrian['status'] == 'menunggu' else "👨‍⚕️" if antrian['status'] == 'dilayani' else "✅"
                rows.append([
                    i,
                    antrian['nomor_antrian'],
                    antrian['nama_lengkap'],
                    f"dr. {antrian['nama_dokter']}",
                    f"{status_icon} {antrian['status'].title()}"
                ])

            print(f"\n--- ANTRIAN POLIKLINIK {pol['nama_poli'].upper()} TANGGAL {tanggal} ---")
            print("\n" + tabulate(rows, headers=headers, tablefmt='grid'))
            print(f"\nTotal antrian: {len(antrians)}")

        except ValueError:
            print("\n❌ Masukkan angka yang valid!")

    @staticmethod
    def update_status_antrian():
        """Update status antrian"""
        print("\n--- UPDATE STATUS ANTRIAN ---")

        antrians = Antrian.get_today_queue()
        if not antrians:
            print("\n📭 Tidak ada antrian hari ini.")
            return

        print("\nDaftar Antrian Hari Ini:")
        for i, antrian in enumerate(antrians, 1):
            status_icon = "⏳" if antrian['status'] == 'menunggu' else "👨‍⚕️" if antrian['status'] == 'dilayani' else "✅"
            print(f"{i}. No. {antrian['nomor_antrian']} - {antrian['nama_lengkap']} ({antrian['nama_poli']}) - {status_icon} {antrian['status'].title()}")

        try:
            choice = int(input("\nPilih antrian (nomor): ")) - 1
            if choice < 0 or choice >= len(antrians):
                print("\n❌ Pilihan tidak valid!")
                return

            antrian = antrians[choice]

            print("\nStatus:")
            print("1. Menunggu")
            print("2. Dilayani")
            print("3. Selesai")

            choice_status = input("\nPilih status baru [1-3]: ")

            status_map = {
                '1': 'menunggu',
                '2': 'dilayani',
                '3': 'selesai'
            }

            if choice_status not in status_map:
                print("\n❌ Pilihan tidak valid!")
                return

            new_status = status_map[choice_status]

            # Buat objek antrian untuk update status
            antrian_obj = Antrian()

            if antrian_obj.update_status(antrian['id'], new_status):
                print(f"\n✅ Status antrian No. {antrian['nomor_antrian']} berhasil diubah menjadi {new_status.title()}!")
            else:
                print("\n❌ Gagal mengupdate status antrian!")

        except ValueError:
            print("\n❌ Masukkan angka yang valid!")

    @staticmethod
    def hapus_antrian():
        """Menghapus antrian"""
        print("\n--- HAPUS ANTRIAN ---")

        antrians = Antrian.get_all()
        if not antrians:
            print("\n📭 Belum ada data antrian.")
            return

        # Tampilkan daftar antrian (batasi 20 terbaru)
        print("\nDaftar Antrian (20 terbaru):")
        for i, antrian in enumerate(antrians[:20], 1):
            status_icon = "⏳" if antrian['status'] == 'menunggu' else "👨‍⚕️" if antrian['status'] == 'dilayani' else "✅"
            print(f"{i}. No. {antrian['nomor_antrian']} - {antrian['nama_lengkap']} ({antrian['tanggal_kunjungan']}) - {status_icon} {antrian['status'].title()}")

        try:
            choice = int(input("\nPilih antrian yang akan dihapus (nomor): ")) - 1
            if choice < 0 or choice >= len(antrians[:20]):
                print("\n❌ Pilihan tidak valid!")
                return

            antrian = antrians[choice]
            confirm = input(f"\n⚠️  Yakin ingin menghapus antrian No. {antrian['nomor_antrian']} - {antrian['nama_lengkap']}? (y/N): ")

            if confirm.lower() == 'y':
                if Antrian.delete(antrian['id']):
                    print(f"\n✅ Antrian No. {antrian['nomor_antrian']} berhasil dihapus!")
                else:
                    print("\n❌ Gagal menghapus antrian!")
            else:
                print("\n❌ Penghapusan dibatalkan.")

        except ValueError:
            print("\n❌ Masukkan angka yang valid!")