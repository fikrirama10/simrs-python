#!/usr/bin/env python3
import os
import sys
import logging
from datetime import datetime, timedelta, timezone

import requests

from database import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def singkron_kondisi():
    # Ensure DB connection
    try:
        if not getattr(db, "connection", None) or not getattr(db.connection, "is_connected", lambda: False)():
            logging.info("🔄 Menghubungkan ke database...")
            if not db.connect():
                logging.error("❌ Gagal terkoneksi ke database!")
                input("\nTekan Enter untuk melanjutkan...")
                return
    except Exception:
        logging.exception("Error saat memeriksa koneksi database.")
        if not db.connect():
            logging.error("❌ Gagal terkoneksi ke database!")
            input("\nTekan Enter untuk melanjutkan...")
            return

    try:
        get_data = db.fetch_query(
            """SELECT 
        rawat.id,
        rawat.idrawat,
        rawat.tglmasuk,
        rawat.tglpulang,
        rawat.icdx,
        rawat.id_encounter,
        rawat.id_condition,
        pasien.nama_pasien,
        pasien.ihs,
        dokter.kode_ihs,
        dokter.nik,
        dokter.nama_dokter,
        organisasi_satusehat.id_location,
        organisasi_satusehat.id_satu_sehat,
        organisasi_satusehat.nama_organisasi,
        demo_detail_rekap_medis.pemeriksaan_fisik
    FROM rawat
    INNER JOIN pasien ON pasien.no_rm = rawat.no_rm
    INNER JOIN dokter ON dokter.id = rawat.iddokter
    INNER JOIN poli ON poli.id = rawat.idpoli
    INNER JOIN organisasi_satusehat ON organisasi_satusehat.id_ruangan = poli.kode
    INNER JOIN demo_rekap_medis on demo_rekap_medis.idrawat = rawat.id
    INNER JOIN demo_detail_rekap_medis on demo_detail_rekap_medis.idrekapmedis = demo_rekap_medis.id
    WHERE pasien.ihs IS NOT NULL 
    AND pasien.ihs != '1'
    AND (rawat.id_encounter IS NOT NULL)
    AND (rawat.id_condition IS NULL OR rawat.id_condition = '')
    AND rawat.icdx IS NOT NULL
    AND rawat.tglmasuk IS NOT NULL
    AND YEAR(rawat.tglmasuk) BETWEEN 2024 AND 2025
    AND rawat.idjenisrawat = 1
    ORDER BY rawat.tglmasuk ASC
    """
        )
    except Exception:
        logging.exception("❌ Gagal menjalankan query fetch data.")
        input("\nTekan Enter untuk melanjutkan...")
        return

    if not get_data:
        logging.info("\n📭 Tidak ada data rawat inap yang perlu disinkronisasi.")
        input("\nTekan Enter untuk melanjutkan...")
        return

    updated = 0
    processed = 0
    for row in get_data:
        processed += 1
        id_condition = row.get("id_condition")
        id_encounter = row.get("id_encounter")
        encounter_identifier_value = row.get("idrawat")

        if id_condition:
            logging.info(
                f"SKIP idrawat={encounter_identifier_value} -> sudah punya id_condition={id_condition}"
            )
            continue

        if not id_encounter:
            logging.warning(
                f"❌ idrawat={encounter_identifier_value} -> id_encounter kosong, lewati."
            )
            continue

        # Parse ICDx safely
        icdx_raw = row.get("icdx") or ""
        if " - " in icdx_raw:
            icd10_code, icd10_display = icdx_raw.split(" - ", 1)
        else:
            # fallback: take full string as code, empty display
            icd10_code = icdx_raw.strip()
            icd10_display = ""

        payload = {
            "clinical_status": "active",
            "category_code": "encounter-diagnosis",
            "icd10_code": icd10_code,
            "icd10_display": icd10_display,
            "patient_id": row.get("ihs"),
            "patient_name": row.get("nama_pasien"),
            "encounter_id": id_encounter,
            "encounter_display": encounter_identifier_value,
            "additional_codes": [],
        }

        headers = {"Content-Type": "application/json"}
        try:
            cek_url = f"http://localhost:8008/api/condition/search-by-encounter/{id_encounter}"
            cek_condisi = requests.get(cek_url, headers=headers, timeout=15)
        except requests.RequestException:
            logging.exception(
                f"❌ idrawat={encounter_identifier_value} -> Gagal meminta cek kondisi ke {cek_url}"
            )
            continue

        if cek_condisi.status_code == 200:
            try:
                data_cek = cek_condisi.json()
            except ValueError:
                logging.warning(
                    f"⚠️ idrawat={encounter_identifier_value} -> Response cek kondisi bukan JSON: {cek_condisi.text}"
                )
                data_cek = {}

            entries = data_cek.get("data", {}).get("entry")
            if isinstance(entries, list) and len(entries) > 0:
                existing_id = entries[0].get("resource", {}).get("id")
                logging.info(
                    f"SKIP idrawat={encounter_identifier_value} -> kondisi sudah ada (id={existing_id})"
                )
                # Update the local DB so we don't reprocess next time
                try:
                    if existing_id:
                        db.execute_query(
                            "UPDATE rawat SET id_condition=%s WHERE id=%s",
                            (existing_id, row.get("id")),
                        )
                        updated += 1
                except Exception:
                    logging.exception(
                        f"⚠️ Gagal menyimpan id_condition={existing_id} untuk idrawat={encounter_identifier_value}"
                    )
                continue

        # Create condition
        try:
            url = "http://localhost:8008/api/condition"
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
        except requests.RequestException:
            logging.exception(
                f"❌ idrawat={encounter_identifier_value} -> Gagal mengirim request POST ke {url}"
            )
            continue

        # Treat any 2xx as success
        if not (200 <= resp.status_code < 300):
            db.execute_query(
                "UPDATE rawat SET id_condition=%s WHERE id=%s",
                (1, row.get("id")),
            )
            logging.error(
                f"❌ idrawat={encounter_identifier_value} -> HTTP {resp.status_code}, body: {resp.text}"
            )
            continue

        try:
            data = resp.json()
        except ValueError:
            logging.warning(
                f"⚠️ idrawat={encounter_identifier_value} -> Response is not valid JSON, body: {resp.text}"
            )
            continue

        # Extract id_condition robustly
        id_condition = None
        resp_data = data.get("data") if isinstance(data, dict) else None
        if isinstance(resp_data, dict):
            # maybe the API returned the resource
            id_condition = resp_data.get("id") or resp_data.get("resource", {}).get("id")
        elif isinstance(resp_data, (str, int)):
            id_condition = str(resp_data)
        else:
            # fallback: try other common shapes
            if isinstance(data, dict):
                possible_id = data.get("id") or data.get("_id")
                if possible_id:
                    id_condition = possible_id

        if not id_condition:
            logging.warning(
                f"⚠️ idrawat={encounter_identifier_value} -> Tidak menemukan id condition pada response: {data}"
            )
            continue

        logging.info(f"✅ idrawat={encounter_identifier_value} -> sukses: id_condition={id_condition}")

        # Persist id_condition back to local DB
        try:
            db.execute_query(
                "UPDATE rawat SET id_condition=%s WHERE id=%s",
                (id_condition, row.get("id")),
            )
            updated += 1
        except Exception:
            logging.exception(
                f"⚠️ Gagal menyimpan id_condition={id_condition} untuk idrawat={encounter_identifier_value}"
            )

    logging.info(
        f"\n📊 Diproses {processed} baris. Berhasil menyimpan id_condition untuk {updated} baris."
    )


if __name__ == "__main__":
    singkron_kondisi()