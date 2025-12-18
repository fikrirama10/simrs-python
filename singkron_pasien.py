import os
import sys
from database import db
import requests
from datetime import datetime


def singkron_pasien():
    # Pastikan database terkoneksi
    if not db.connection or not db.connection.is_connected():
        print("🔄 Menghubungkan ke database...")
        if not db.connect():
            print("❌ Gagal terkoneksi ke database!")
            input("\nTekan Enter untuk melanjutkan...")
            return

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
            print(data['data']['entry'][0]['resource']['id'])
            update = db.execute_query("""
            UPDATE pasien SET ihs=%s WHERE id=%s
            """, (data['data']['entry'][
                0]['resource']['id'], pid))
            if update:
                updated += 1

            print(f"✅ nik={nik} -> Data ditemukan dari Satu Sehat.")
            print(data['data']['entry'][0]['resource']['id'])
            print(updated)
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


if __name__ == "__main__":
    singkron_pasien()