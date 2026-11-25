@echo off
echo =================================================================
echo  Launching Real-Time Traffic Violation System (Backend + Frontend)
echo =================================================================
cd /d "%~dp0\.."

start "Traffic AI Backend" cmd /k "scripts\run_backend.bat"
timeout /t 3
start "Traffic UI Dashboard" cmd /k "scripts\run_frontend.bat"

echo System launching!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:5173
