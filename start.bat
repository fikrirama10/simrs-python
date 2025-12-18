@echo off
title SIMRS - Sistem Informasi Manajemen Rumah Sakit

echo ========================================
echo    SIMRS - Sistem Informasi Manajemen
echo           Rumah Sakit
echo ========================================
echo.

REM Cek apakah venv ada
if not exist "venv" (
    echo Virtual environment tidak ditemukan!
    echo Membuat virtual environment...
    python -m venv venv
    echo.
)

REM Aktifkan virtual environment
echo Mengaktifkan virtual environment...
call venv\Scripts\activate

REM Cek dependencies
echo Memeriksa dependencies...
pip show mysql-connector-python >nul 2>&1
if errorlevel 1 (
    echo Menginstall dependencies...
    pip install -r requirements.txt
    echo.
)

echo Starting SIMRS...
echo.
python main.py

pause