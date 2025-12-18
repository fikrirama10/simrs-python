#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from database import db
from crud_operations import CRUDOperations
import requests
from datetime import datetime

class SIMRS:
    """Sistem Informasi Manajemen Rumah Sakit"""

    def __init__(self):
        self.connected = False

    def clear_screen(self):
        """Membersihkan layar console"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        """Menampilkan banner aplikasi"""
        self.clear_screen()
        print("="*60)
        print("     SISTEM INFORMASI MANAJEMEN RUMAH SAKIT (SIMRS)")
        print("="*60)
        print("      Sederhana - Python + MySQL")
        print("="*60)
        print()

    def check_connection(self):
        """Memeriksa koneksi database"""
        if not self.connected:
            print("🔄 Menghubungkan ke database...")
            self.connected = db.connect()
            if not self.connected:
                print("\n❌ Tidak dapat terkoneksi ke database!")
                print("Silakan periksa konfigurasi database Anda.")
                return False
        return True

    def initialize_database(self):
        """Inisialisasi database dan tabel"""
        print("🔧 Mempersiapkan database...")
        db.create_database_and_tables()
        return True

    def main_menu(self):
        """Menu utama aplikasi"""
        while True:
            self.show_banner()
            print("MENU UTAMA:")
            print("1. 🏥 Manajemen Pasien")
            print("2. 👨‍⚕️  Manajemen Dokter")
            print("3. 🏢 Manajemen Poliklinik")
            print("4. 📋 Manajemen Antrian")
            print("5. 📊 Laporan & Statistik")
            print("6. 🔄 Sinkronisasi Satu Sehat")
            print("7. ⚙️  Pengaturan Koneksi")
            print("0. 🚪 Keluar")
            print()

            choice = input("Pilih menu [0-7]: ").strip()

            if choice == '1':
                if self.check_connection():
                    CRUDOperations.pasien_menu()
                else:
                    self.setup_connection()

            elif choice == '2':
                if self.check_connection():
                    CRUDOperations.dokter_menu()
                else:
                    self.setup_connection()

            elif choice == '3':
                if self.check_connection():
                    CRUDOperations.poliklinik_menu()
                else:
                    self.setup_connection()

            elif choice == '4':
                if self.check_connection():
                    CRUDOperations.antrian_menu()
                else:
                    self.setup_connection()

            elif choice == '5':
                if self.check_connection():
                    self.laporan_menu()
                else:
                    self.setup_connection()

            elif choice == '6':
                if self.check_connection():
                    self.singkron_pasien()
                else:
                    self.setup_connection()

            elif choice == '7':
                self.setup_connection()

            elif choice == '0':
                self.exit_application()

            else:
                print("\n❌ Pilihan tidak valid. Silakan coba lagi.")
                input("\nTekan Enter untuk melanjutkan...")

    def laporan_menu(self):
        """Menu laporan dan statistik"""
        from tabulate import tabulate
        from models import Pasien, Dokter, Poliklinik, Antrian


        while True:
            self.clear_screen()
            print("="*50)
            print("         LAPORAN & STATISTIK")
            print("="*50)
            print("1. 📈 Statistik Umum")
            print("2. 👥 Laporan Pasien")
            print("3. 📊 Laporan Antrian Hari Ini")
            print("4. 🏆 Top Poliklinik Terpadat")
            print("0. Kembali ke Menu Utama")

            choice = input("\nPilih menu [0-4]: ")

            if choice == '1':
                print("\n--- STATISTIK UMUM ---")
                total_pasien = len(Pasien.get_all() or [])
                total_dokter = len(Dokter.get_all() or [])
                total_poliklinik = len(Poliklinik.get_all() or [])
                total_antrian = len(Antrian.get_all() or [])
                antrian_hari_ini = len(Antrian.get_today_queue() or [])

                data = [
                    ["Total Pasien", f"{total_pasien} orang"],
                    ["Total Dokter", f"{total_dokter} orang"],
                    ["Total Poliklinik", f"{total_poliklinik} poli"],
                    ["Total Semua Antrian", f"{total_antrian} antrian"],
                    ["Antrian Hari Ini", f"{antrian_hari_ini} antrian"]
                ]

                print("\n" + tabulate(data,
                      headers=["Keterangan", "Jumlah"], tablefmt="grid"))

            elif choice == '2':
                print("\n--- LAPORAN PASIEN ---")
                pasiens = Pasien.get_all()
                if pasiens:
                    # Statistik jenis kelamin
                    l = sum(1 for p in pasiens if p['jenis_kelamin'] == 'L')
                    p = sum(1 for p in pasiens if p['jenis_kelamin'] == 'P')

                    print(f"\n📊 Statistik Pasien:")
                    print(f"   Total: {len(pasiens)} pasien")
                    print(f"   Laki-laki: {l} pasien")
                    print(f"   Perempuan: {p} pasien")
                else:
                    print("\n📭 Belum ada data pasien.")

            elif choice == '3':
                print("\n--- LAPORAN ANTRIAN HARI INI ---")
                antrians = Antrian.get_today_queue()
                if antrians:
                    # Statistik status
                    menunggu = sum(
                        1 for a in antrians if a['status'] == 'menunggu')
                    dilayani = sum(
                        1 for a in antrians if a['status'] == 'dilayani')
                    selesai = sum(
                        1 for a in antrians if a['status'] == 'selesai')

                    data = [
                        ["Menunggu", f"⏳ {menunggu} antrian"],
                        ["Sedang Dilayani", f"👨‍⚕️ {dilayani} antrian"],
                        ["Selesai", f"✅ {selesai} antrian"],
                        ["Total", f"📋 {len(antrians)} antrian"]
                    ]

                    print("\n" + tabulate(data,
                          headers=["Status", "Jumlah"], tablefmt="grid"))
                else:
                    print("\n📭 Tidak ada antrian hari ini.")

            elif choice == '4':
                print("\n--- TOP POLIKLINIK TERPADAT ---")
                # Query untuk menghitung antrian per poliklinik
                query = """
                SELECT p.nama_poli, COUNT(a.id) as total_antrian
                FROM poliklinik p
                LEFT JOIN antrian a ON p.id = a.id_poliklinik
                GROUP BY p.id, p.nama_poli
                ORDER BY total_antrian DESC
                LIMIT 5
                """
                result = db.fetch_query(query)

                if result:
                    headers = ["Poliklinik", "Total Antrian"]
                    rows = [[r['nama_poli'], r['total_antrian']]
                        for r in result]
                    print("\n" + tabulate(rows, headers=headers, tablefmt="grid"))
                else:
                    print("\n📭 Belum ada data antrian.")

            elif choice == '0':
                break

            else:
                print("\n❌ Pilihan tidak valid.")

            if choice != '0':
                input("\nTekan Enter untuk melanjutkan...")

    def setup_connection(self):
        """Setup koneksi database"""
        self.clear_screen()
        print("="*50)
        print("      PENGATURAN KONEKSI DATABASE")
        print("="*50)
        print()

        print("1. Gunakan konfigurasi default")
        print("2. Masukkan konfigurasi manual")
        print("0. Kembali")

        choice = input("\nPilih [0-2]: ")

        if choice == '1':
            # Coba koneksi dengan default
            self.connected = db.connect()
            if self.connected:
                print("\n✅ Berhasil terkoneksi dengan konfigurasi default!")
                input("\nTekan Enter untuk melanjutkan...")
            else:
                print("\n❌ Gagal terkoneksi. Silakan masukkan konfigurasi manual.")
                input("\nTekan Enter untuk melanjutkan...")

        elif choice == '2':
            print("\nMasukkan detail koneksi database:")
            print("(Kosongkan untuk menggunakan nilai default)")

            db.host = input(f"Host [{db.host}]: ") or db.host
            db.port = input(f"Port [{db.port}]: ") or db.port
            db.user = input(f"Username [{db.user}]: ") or db.user
            db.password = input(f"Password: ") or db.password
            db.database = input(f"Database [{db.database}]: ") or db.database

            self.connected = db.connect()
            if self.connected:
                print("\n✅ Koneksi berhasil!")
                # Simpan ke .env file
                self.save_env_config()
                input("\nTekan Enter untuk melanjutkan...")
            else:
                print("\n❌ Koneksi gagal. Periksa kembali konfigurasi Anda.")
                input("\nTekan Enter untuk melanjutkan...")

    def save_env_config(self):
        """Menyimpan konfigurasi ke file .env"""
        try:
            with open('.env', 'w') as f:
                f.write(f"DB_HOST={db.host}\n")
                f.write(f"DB_PORT={db.port}\n")
                f.write(f"DB_USER={db.user}\n")
                f.write(f"DB_PASSWORD={db.password}\n")
                f.write(f"DB_NAME={db.database}\n")
            print("✅ Konfigurasi disimpan ke file .env")
        except Exception as e:
            print(f"⚠️  Gagal menyimpan konfigurasi: {e}")

    def singkron_pasien(self):
        get_data = db.fetch_query("""
        SELECT id,no_rm,nik,nama_pasien,ihs FROM pasien
        WHERE ihs IS NULL AND nik IS NOT NULL AND nik != ''
        ORDER BY tgldaftar DESC
        """)
        if not get_data:
            print("\n📭 Tidak ada pasien yang perlu disinkronisasi.")
            input("\nTekan Enter untuk melanjutkan...")
            return
        updated = 0
        for row in get_data:
            nik = row.get('nik')
            pid = row.get('id')
            if not nik:
                continue
            try:
                url = f"http://localhost:8008/api/patient/search-by-nik/{nik}"
                resp = requests.get(url, timeout=8)
                if resp.status_code != 200:
                    print(f"❌ nik={nik} -> HTTP {resp.status_code}")
                    continue

                data = resp.json()

                update = db.execute_query("""
                UPDATE pasien SET ihs=%s WHERE id=%s
                """, (data['data']['entry'][0]['resource']['id'], pid))
                if update:
                    updated += 1

                print(f"✅ nik={nik} -> Data ditemukan dari Satu Sehat.")
                print(data['data']['entry'][0]['resource']['id'])
                print(updated)
                # Coba ekstrak nilai id/nomor IHS dari respons
                # ihs_value = None
                # if isinstance(data, dict):
                #     for key in ('ihs','nomorIhs','nomorIHS','noIhs','id','patient_id','_id'):
                #         if key in data and data[key]:
                #             ihs_value = data[key]
                #             break
                #     if ihs_value is None:
                #         for container in ('data','response','result'):
                #             if container in data and isinstance(data[container], dict):
                #                 for key in ('ihs','nomorIhs','nomorIHS','noIhs','id','patient_id','_id'):
                #                     if key in data[container] and data[container][key]:
                #                         ihs_value = data[container][key]
                #                         break
                #                 if ihs_value:
                #                     break

                # # Fallback: simpan seluruh JSON jika tidak ditemukan field spesifik
                # if ihs_value is None:
                #     ihs_value = resp.text

                # # Simpan ke database
                # try:
                #     db.execute("UPDATE pasien SET ihs=%s WHERE id=%s", (ihs_value, pid))
                #     updated += 1
                #     print(f"✅ Pasien id={pid} nik={nik} diperbarui.")
                # except Exception as e:
                #     print(f"⚠️ Gagal menyimpan untuk nik={nik}: {e}")

            except Exception as e:
                update = db.execute_query("""
                UPDATE pasien SET ihs=%s WHERE id=%s
                """, (1, pid))
                print(f"❌ nik={nik} -> {e}")

        print(f"\n📌 Selesai. Total pasien diperbarui: {updated}")
        print(f"\n📊 Ditemukan {len(get_data)} pasien yang belum tersinkronisasi.")
        print("\n" + "="*120)
        print(get_data)

        print("="*120)
        input("\nTekan Enter untuk melanjutkan...")

    def exit_application(self):
        """Keluar dari aplikasi"""
        self.clear_screen()
        print("="*50)
        print("      TERIMA KASIH")
        print("="*50)
        print("   SIMRS - Sistem Informasi Manajemen Rumah Sakit")
        print("   Version 1.0")
        print("="*50)
        print()

        if self.connected:
            print("🔄 Menutup koneksi database...")
            db.disconnect()

        print("👋 Sampai jumpa!")
        sys.exit(0)

    def run(self):
        """Menjalankan aplikasi"""
        try:
            self.show_banner()
            print("🚀 Memulai SIMRS...")

            # Coba koneksi ke database
            if self.check_connection():
                # Inisialisasi database dan tabel
                self.initialize_database()

            # Masuk ke menu utama
            self.main_menu()

        except KeyboardInterrupt:
            print("\n\n⚠️  Program dihentikan oleh user.")
            self.exit_application()
        except Exception as e:
            print(f"\n❌ Terjadi kesalahan: {e}")
            input("\nTekan Enter untuk keluar...")
            self.exit_application()

def main():
    """Fungsi main untuk menjalankan aplikasi"""
    app = SIMRS()
    app.run()

if __name__ == "__main__":
    main()