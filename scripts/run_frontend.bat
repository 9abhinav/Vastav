@echo off
echo ===================================================
echo Starting Traffic Violation React Frontend...
echo ===================================================
cd /d "%~dp0\..\frontend"

if not exist "node_modules\" (
    echo Installing node dependencies...
    npm install
)

npm run dev
pause
