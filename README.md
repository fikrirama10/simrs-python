# SIMRS - Sistem Informasi Manajemen Rumah Sakit

Aplikasi sederhana berbasis Python untuk mengelola data rumah sakit dengan database MySQL.

## Fitur

### 📋 Fitur Utama
- **Manajemen Pasien**: Tambah, lihat, update, hapus data pasien
- **Manajemen Dokter**: Tambah, lihat, update, hapus data dokter
- **Manajemen Poliklinik**: Tambah, lihat, update, hapus data poliklinik
- **Manajemen Antrian**: Sistem antrian pasien dengan nomor otomatis
- **Laporan & Statistik**: Berbagai laporan dan statistik data
- **Multi-user Support**: Support multiple concurrent users

### 🏥 Detail Fitur

#### Pasien Management
- Input data pasien lengkap (RM, nama, tanggal lahir, dll)
- Pencarian pasien berdasarkan nama atau nomor RM
- Update data pasien
- Hapus data pasien dengan konfirmasi

#### Dokter Management
- Input data dokter dengan SIP
- Spesialisasi dokter
- Kontak dokter
- Update dan hapus data

#### Poliklinik Management
- Input data poliklinik
- Lokasi (gedung dan lantai)
- Update dan hapus data

#### Antrian System
- Nomor antrian otomatis per poliklinik
- Status tracking (menunggu, dilayani, selesai)
- Filter per poliklinik dan tanggal
- Update status antrian

#### Reporting
- Statistik umum (total pasien, dokter, dll)
- Laporan pasien
- Laporan antrian harian
- Top poliklinik terpadat

## Requirements

- Python 3.7+
- MySQL Server 5.7+ atau 8.0+
- Library Python (lihat requirements.txt)

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd simrs
```

### 2. Setup Virtual Environment (Disarankan)
```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Database MySQL
Pastikan MySQL Server sudah terinstall dan running.

### 4. Konfigurasi Database
Salin file `.env.example` menjadi `.env`:
```bash
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

Edit file `.env` sesuai konfigurasi MySQL Anda:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=simrs
```

### 5. Jalankan Aplikasi

#### Cara 1: Menggunakan Batch File (Windows)
```bash
# Double-click atau jalankan dari command prompt
start.bat
```

#### Cara 2: Manual
```bash
# Aktifkan venv terlebih dahulu
venv\Scripts\activate

# Jalankan aplikasi
python main.py
```

## Database Schema

### Tables

1. **pasien**
   - id (PK, Auto Increment)
   - nomor_rm (Unique)
   - nama_lengkap
   - tanggal_lahir
   - jenis_kelamin (L/P)
   - alamat
   - nomor_telepon
   - created_at

2. **dokter**
   - id (PK, Auto Increment)
   - nomor_sip (Unique)
   - nama_dokter
   - spesialisasi
   - nomor_telepon
   - created_at

3. **poliklinik**
   - id (PK, Auto Increment)
   - nama_poli (Unique)
   - gedung
   - lantai
   - created_at

4. **antrian**
   - id (PK, Auto Increment)
   - nomor_antrian
   - id_pasien (FK)
   - id_dokter (FK)
   - id_poliklinik (FK)
   - tanggal_kunjungan
   - keluhan
   - status (menunggu/dilayani/selesai)
   - created_at

## Usage

### Menjalankan Aplikasi
1. Pastikan MySQL Server running
2. Konfigurasi koneksi database di menu pengaturan
3. Aplikasi akan otomatis membuat database dan tabel yang diperlukan
4. Mulai input data melalui menu yang tersedia

### Menu Navigasi
- Gunakan angka untuk memilih menu
- Enter untuk konfirmasi
- y/N untuk konfirmasi hapus
- Ctrl+C untuk keluar darurat

## File Structure

```
simrs/
├── main.py              # File utama aplikasi
├── database.py          # Koneksi dan operasi database
├── models.py            # Model data (Pasien, Dokter, Poliklinik, Antrian)
├── crud_operations.py   # Operasi CRUD dan menu
├── requirements.txt     # Dependencies Python
├── .env.example         # Contoh konfigurasi environment
├── start.bat           # Batch file untuk menjalankan aplikasi (Windows)
├── venv/               # Virtual environment folder
└── README.md           # Documentation
```

## Development

### Menambah Fitur Baru
1. Tambah model di `models.py`
2. Tambah operasi CRUD di `crud_operations.py`
3. Tambah menu di `main.py`

### Testing
```bash
# Test koneksi database
python -c "from database import db; db.connect()"

# Test model
python -c "from models import Pasien; print(Pasien.get_all())"
```

## Troubleshooting

### Common Issues

1. **Connection Error**
   - Pastikan MySQL Server running
   - Cek username/password di `.env`
   - Pastikan database ada atau user punya hak CREATE

2. **Module Not Found**
   - Install dependencies: `pip install -r requirements.txt`

3. **Permission Denied**
   - Cek hak akses user MySQL ke database
   - Pastikan user bisa CREATE TABLE

4. **Port Already in Use**
   - Cek port MySQL: `netstat -an | findstr 3306` (Windows) atau `netstat -an | grep 3306` (Linux/Mac)

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License - lihat file LICENSE untuk detail

## Author

- Nama: [Your Name]
- Email: [your.email@example.com]
- GitHub: [username]

## Version History

- v1.0.0 - Initial Release
  - Basic CRUD operations
  - Antrian system
  - Reporting features
  - MySQL integration