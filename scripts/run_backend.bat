@echo off
echo ===================================================
echo Starting Traffic Violation AI Backend Server...
echo ===================================================
cd /d "%~dp0\.."

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python scripts\setup_db.py
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause
