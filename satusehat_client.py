import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class SatuSehatClient:
    """Client untuk mengakses API Satu Sehat"""

    def __init__(self):
        self.base_url = os.getenv('SATUSEHAT_BASE_URL', 'https://api-satusehat.kemkes.go.id')
        self.auth_url = os.getenv('SATUSEHAT_AUTH_URL', 'https://api-satusehat.kemkes.go.id/oauth2/v1')
        self.client_id = os.getenv('SATUSEHAT_CLIENT_ID')
        self.client_secret = os.getenv('SATUSEHAT_CLIENT_SECRET')
        self.organization_id = os.getenv('SATUSEHAT_ORGANIZATION_ID')

        self.access_token = None
        self.token_expires_at = None

    def get_access_token(self):
        """Mendapatkan access token dari OAuth2 Satu Sehat"""
        # Check if current token is still valid
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        if not self.client_id or not self.client_secret:
            raise ValueError("SATUSEHAT_CLIENT_ID dan SATUSEHAT_CLIENT_SECRET harus diisi di file .env")

        try:
            # Request token
            auth_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.post(
                f"{self.auth_url}/accesstoken?grant_type=client_credentials",
                data=auth_data,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)

                # Set expiry time (dengan buffer 5 menit sebelum expired)
                self.token_expires_at = datetime.now().timestamp() + expires_in - 300

                print("✅ Berhasil mendapatkan access token Satu Sehat")
                return self.access_token
            else:
                print(f"❌ Gagal mendapatkan token: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error saat request token: {e}")
            return None
        except Exception as e:
            print(f"❌ Error mendapatkan access token: {e}")
            return None

    def get_headers(self):
        """Mendapatkan headers untuk API request"""
        token = self.get_access_token()
        if not token:
            raise Exception("Gagal mendapatkan access token")

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def get_patient_by_nik(self, nik):
        """Mendapatkan data pasien dari Satu Sehat berdasarkan NIK"""
        if not nik or len(nik) != 16:
            print(f"❌ NIK tidak valid: {nik}")
            return None

        try:
            headers = self.get_headers()

            # Endpoint untuk mencari pasien berdasarkan NIK
            url = f"{self.base_url}/fhir-r4/v1/Patient?identifier=https://fhir.kemkes.go.id/id/nik|{nik}"

            print(f"🔍 Mencari pasien dengan NIK: {nik}")

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if 'entry' in data and len(data['entry']) > 0:
                    patient = data['entry'][0]['resource']

                    # Extract IHS number
                    ihs_number = patient.get('id')

                    # Extract patient data
                    patient_data = {
                        'ihs_number': ihs_number,
                        'name': '',
                        'birth_date': patient.get('birthDate', ''),
                        'gender': patient.get('gender', ''),
                        'nik': nik
                    }

                    # Get name
                    if 'name' in patient and len(patient['name']) > 0:
                        name_data = patient['name'][0]
                        if 'text' in name_data:
                            patient_data['name'] = name_data['text']
                        elif 'given' in name_data and 'family' in name_data:
                            given_names = ' '.join(name_data['given'])
                            patient_data['name'] = f"{given_names} {name_data['family']}"

                    print(f"✅ Ditemukan pasien: {patient_data['name']} (IHS: {ihs_number})")
                    return patient_data
                else:
                    print(f"❌ Pasien dengan NIK {nik} tidak ditemukan di Satu Sehat")
                    return None

            elif response.status_code == 404:
                print(f"❌ Pasien dengan NIK {nik} tidak ditemukan (404)")
                return None
            elif response.status_code == 401:
                print("❌ Token tidak valid, refresh token...")
                self.access_token = None
                self.token_expires_at = None
                # Retry dengan token baru
                return self.get_patient_by_nik(nik)
            else:
                print(f"❌ Error API: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error saat request ke API: {e}")
            return None
        except Exception as e:
            print(f"❌ Error mendapatkan data pasien: {e}")
            return None

    def create_patient(self, patient_data):
        """Membuat pasien baru di Satu Sehat (jika belum ada)"""
        try:
            headers = self.get_headers()

            # Format FHIR Patient resource
            fhir_patient = {
                "resourceType": "Patient",
                "identifier": [
                    {
                        "system": "https://fhir.kemkes.go.id/id/nik",
                        "value": patient_data['nik']
                    }
                ],
                "name": [
                    {
                        "use": "official",
                        "text": patient_data['nama_lengkap']
                    }
                ],
                "gender": "male" if patient_data.get('jenis_kelamin') == 'L' else "female",
                "birthDate": patient_data.get('tanggal_lahir'),
                "managingOrganization": {
                    "reference": f"Organization/{self.organization_id}"
                }
            }

            url = f"{self.base_url}/fhir-r4/v1/Patient"

            response = requests.post(url, headers=headers, json=fhir_patient, timeout=30)

            if response.status_code == 201:  # Created
                created_patient = response.json()
                ihs_number = created_patient.get('id')
                print(f"✅ Berhasil membuat pasien di Satu Sehat (IHS: {ihs_number})")
                return {
                    'ihs_number': ihs_number,
                    'name': patient_data['nama_lengkap'],
                    'nik': patient_data['nik'],
                    'birth_date': patient_data.get('tanggal_lahir'),
                    'gender': fhir_patient['gender']
                }
            else:
                print(f"❌ Gagal membuat pasien: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error membuat pasien: {e}")
            return None

# Global instance
satusehat = SatuSehatClient()