import os
import sys
from database import db
import requests
from datetime import datetime, timedelta, timezone
import json
import traceback

def parse_number_string(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return s
    if not isinstance(s, str):
        return s
    s2 = s.strip().replace(',', '.')
    # coba int dahulu jika tidak mengandung titik, selain itu float
    try:
        if '.' in s2:
            return float(s2)
        else:
            return int(s2)
    except ValueError:
        # kembalikan string asli bila tidak bisa konversi
        return s

# clamp tanggal agar berada di rentang yang diizinkan oleh server FHIR
MIN_ALLOWED = datetime(2014, 6, 3, tzinfo=timezone.utc)

def to_utc_iso(dt):
    """Terima datetime atau string. Kembalikan ISO8601 UTC dengan Z."""
    if dt is None:
        return None
    # jika string, coba parse beberapa format umum
    if isinstance(dt, str):
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                parsed = datetime.strptime(dt, fmt)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                dt = parsed
                break
            except Exception:
                parsed = None
        if parsed is None:
            # fallback: ignore timezone, treat as naive UTC
            try:
                parsed = datetime.fromisoformat(dt)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                dt = parsed
            except Exception:
                # tidak bisa parse
                return None

    # jika objek datetime
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    else:
        return None

    now = datetime.now(timezone.utc)
    if dt < MIN_ALLOWED:
        return MIN_ALLOWED.isoformat().replace("+00:00", "Z")
    if dt > now:
        return now.isoformat().replace("+00:00", "Z")
    return dt.isoformat().replace("+00:00", "Z")


def singkron_rawat():
    if not db.connection or not db.connection.is_connected():
        print("🔄 Menghubungkan ke database...")
        if not db.connect():
            print("❌ Gagal terkoneksi ke database!")
            input("\nTekan Enter untuk melanjutkan...")
            return

    get_data = db.fetch_query("""
    SELECT 
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
    AND (rawat.id_encounter IS NULL OR rawat.id_encounter = '')
    AND rawat.tglmasuk IS NOT NULL
    AND YEAR(rawat.tglmasuk) BETWEEN 2024 AND 2025
    AND rawat.idjenisrawat = 1
    ORDER BY rawat.tglmasuk DESC
    """)

    if not get_data:
        print("\n📭 Tidak ada pasien yang perlu disinkronisasi.")
        input("\nTekan Enter untuk melanjutkan...")
        return

    updated = 0
    for row in get_data:
        try:
            patient_id = row.get('ihs')
            patient_name = row.get('nama_pasien')
            practitioner_id = row.get('kode_ihs')
            practitioner_name = row.get('nama_dokter')
            organization_id = '100026488'
            encounter_identifier_system = 'http://sys-ids.kemkes.go.id/encounter/100026488'
            encounter_identifier_value = row.get('idrawat')
            encounter_class_code = 'AMB'
            encounter_class_display = 'ambulatory'

            # tglmasuk / tglpulang kemungkinan datetime dari DB (naive)
            tglmasuk_raw = row.get('tglmasuk')
            tglpulang_raw = row.get('tglpulang')

            # Buat period_start / period_end sebagai ISO UTC dengan Z, clamp ke rentang yang diperbolehkan
            period_start = to_utc_iso(tglmasuk_raw)
            if not period_start:
                # jika tidak bisa parse, gunakan now sebagai fallback (dan catat)
                period_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                print(f"⚠️ idrawat={encounter_identifier_value}: tglmasuk tidak valid, menggunakan NOW.")

            # period_end: jika ada tglpulang gunakan, kalau tidak set 3 jam setelah tglmasuk
            if tglpulang_raw:
                period_end = to_utc_iso(tglpulang_raw)
            else:
                # buat dari tglmasuk_raw (cari object datetime)
                if isinstance(tglmasuk_raw, datetime):
                    pe = (tglmasuk_raw.replace(tzinfo=timezone.utc) if tglmasuk_raw.tzinfo is None else tglmasuk_raw) + timedelta(hours=3)
                    period_end = to_utc_iso(pe)
                else:
                    period_end = to_utc_iso(datetime.now(timezone.utc) + timedelta(hours=3))

            # safety: pastikan period_end >= period_start
            try:
                ps_dt = datetime.fromisoformat(period_start.replace("Z", "+00:00"))
                pe_dt = datetime.fromisoformat(period_end.replace("Z", "+00:00"))
                if pe_dt < ps_dt:
                    pe_dt = ps_dt + timedelta(hours=3)
                    period_end = pe_dt.isoformat().replace("+00:00", "Z")
            except Exception:
                # jika parse gagal, biarkan apa adanya
                pass

            location_id = row.get('id_location') or row.get('id_location')
            location_display = row.get('nama_organisasi')

            # parsing pemeriksaan_fisik (bisa string JSON atau dict)
            pemeriksaan_fisik = row.get('pemeriksaan_fisik')
            if isinstance(pemeriksaan_fisik, str):
                try:
                    pemeriksaan_fisik = json.loads(pemeriksaan_fisik)
                except Exception:
                    # jika JSON invalid, coba eval aman (tidak dianjurkan), atau set None
                    try:
                        pemeriksaan_fisik = json.loads(pemeriksaan_fisik.replace("'", '"'))
                    except Exception:
                        print(f"⚠️ idrawat={encounter_identifier_value}: pemeriksaan_fisik tidak dapat di-parse, nilai asli: {row.get('pemeriksaan_fisik')}")
                        pemeriksaan_fisik = {}

            if pemeriksaan_fisik is None:
                pemeriksaan_fisik = {}

            # Pisah tekanan darah
            td = pemeriksaan_fisik.get('tekanan_darah') or pemeriksaan_fisik.get('tekanan-darah') or pemeriksaan_fisik.get('blood_pressure')
            if isinstance(td, str) and '/' in td:
                try:
                    systolic_s, diastolic_s = td.split('/', 1)
                    systolic = parse_number_string(systolic_s)
                    diastolic = parse_number_string(diastolic_s)
                    # pastikan int jika memungkinkan
                    try:
                        systolic = int(systolic)
                    except Exception:
                        pass
                    try:
                        diastolic = int(diastolic)
                    except Exception:
                        pass
                    pemeriksaan_fisik['sistolik'] = systolic
                    pemeriksaan_fisik['diastolik'] = diastolic
                except Exception:
                    pemeriksaan_fisik['sistolik'] = None
                    pemeriksaan_fisik['diastolik'] = None

            # Konversi field numeric lainnya dengan normalisasi koma->titik dulu
            int_fields = ['nadi', 'pernapasan', 'berat_badan', 'tinggi_badan', 'spo2']
            float_fields = ['suhu', 'bmi']

            for k in int_fields:
                if k in pemeriksaan_fisik:
                    val = parse_number_string(pemeriksaan_fisik.get(k))
                    try:
                        pemeriksaan_fisik[k] = int(val) if val is not None else None
                    except Exception:
                        pemeriksaan_fisik[k] = val  # tinggalkan apa adanya jika tidak bisa cast

            for k in float_fields:
                if k in pemeriksaan_fisik:
                    val = parse_number_string(pemeriksaan_fisik.get(k))
                    try:
                        pemeriksaan_fisik[k] = float(val) if val is not None else None
                    except Exception:
                        pemeriksaan_fisik[k] = val

            # Ambil nilai yang diperlukan untuk payload
            temperature = pemeriksaan_fisik.get('suhu') if pemeriksaan_fisik.get('suhu') is not None else 36
            heart_rate = pemeriksaan_fisik.get('nadi') if pemeriksaan_fisik.get('nadi') is not None else 80
            respiratory_rate = pemeriksaan_fisik.get('pernapasan') if pemeriksaan_fisik.get('pernapasan') is not None else 20
            systolic_bp = pemeriksaan_fisik.get('sistolik') if pemeriksaan_fisik.get('sistolik') is not None else 120
            diastolic_bp = pemeriksaan_fisik.get('diastolik')   if pemeriksaan_fisik.get('diastolik') is not None else 80
            data_payload = {
                patient_id,
                patient_name,
                practitioner_id,
                practitioner_name,
                organization_id,
                encounter_identifier_system,
                encounter_identifier_value,
                encounter_class_code,
                encounter_class_display,
                period_start,
                period_end,
                location_id,
                location_display,
                temperature,
                heart_rate,
                respiratory_rate,
                systolic_bp,
                diastolic_bp                
            }
            # print(f"ℹ️ idrawat={encounter_identifier_value} payload vital signs:", data_payload)
            # continue
            consent_action = 'OPTIN'
            consent_agent = 'System'
            skip_consent = False
            skip_vital_signs = False
            skip_conditions = False
            auto_finish_encounter = False
            diagnosis_list = []
            # tetap kosong kecuali ada mapping ICDX

            url = f"http://localhost:8008/api/workflow/complete-visit"
            resp = requests.post(url, json={
                "patient_id": patient_id,
                "patient_name": patient_name,
                "practitioner_id": practitioner_id,
                "practitioner_name": practitioner_name,
                "organization_id": organization_id,
                "encounter_identifier_system": encounter_identifier_system,
                "encounter_identifier_value": encounter_identifier_value,
                "encounter_class_code": encounter_class_code,
                "encounter_class_display": encounter_class_display,
                "period_start": period_start,
                "period_end": period_end,
                "location_id": location_id,
                "location_display": location_display,
                "diagnosis_list": diagnosis_list,
                "temperature": temperature,
                "heart_rate": heart_rate,
                "respiratory_rate": respiratory_rate,
                "systolic_bp": systolic_bp,
                "diastolic_80p": diastolic_bp,   # menjaga nama field lama jika API mengharapkannya
                "consent_action": consent_action,
                "consent_agent": consent_agent,
                "skip_consent": skip_consent,
                "skip_vital_signs": skip_vital_signs,
                "skip_conditions": skip_conditions,
                "auto_finish_encounter": auto_finish_encounter
            }, timeout=15)

            if resp.status_code != 200:
                body = None
                try:
                    body = resp.text
                except Exception:
                    body = "<unable to read response body>"
                print(f"❌ idrawat={encounter_identifier_value} -> HTTP {resp.status_code} {getattr(resp, 'reason', '')}\nResponse body: {body}")
                # jika server mengembalikan OperationOutcome di body, coba tampilkan issue-nya
                try:
                    parsed = resp.json()
                    if isinstance(parsed, dict) and parsed.get('resourceType') == 'OperationOutcome':
                        issues = parsed.get('issue', [])
                        for issue in issues:
                            print("  OperationOutcome:", issue.get('details', {}).get('text'), "expr:", issue.get('expression'))
                except Exception:
                    pass
                continue

            try:
                data = resp.json()
            except ValueError:
                print(f"⚠️ idrawat={encounter_identifier_value} -> Response is not valid JSON, body: {resp.text}")
                continue

            # Extract encounter id defensively from multiple possible response shapes
            id_encounter = None
            try:
                if isinstance(data, dict):
                    top = data
                    inner = top.get('data') or {}
                    # primary expected path
                    id_encounter = inner.get('consent', {}).get('data', {}).get('id')
                    # fallback to encounter path
                    if not id_encounter:
                        id_encounter = inner.get('encounter', {}).get('encounter_id')
                    # other possible shapes: consent/encounter at top level
                    if not id_encounter:
                        id_encounter = top.get('consent', {}).get('data', {}).get('id') or top.get('encounter', {}).get('encounter_id')
                    # last resort: any top-level id
                    if not id_encounter:
                        id_encounter = top.get('id')
            except Exception:
                id_encounter = None

            print(f"    id_encounter: {id_encounter}")  
            print(f"✅ idrawat={encounter_identifier_value} -> sukses:", id_encounter)
           
            db.execute_query("""
            UPDATE rawat SET id_encounter=%s WHERE id=%s
            """, (id_encounter if id_encounter is not None else None, row.get('id')))
            updated += 1

        except Exception:
            traceback.print_exc()
            continue

    print(f"\n📊 Ditemukan {len(get_data)} pasien yang belum tersinkronisasi. Berhasil dikirim: {updated}")

singkron_rawat()