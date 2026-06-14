@echo off
echo Starting SQLAgent-Mini-Project...
echo.

echo [1/1] Starting FastAPI server (API + Frontend) on http://127.0.0.1:8001
echo       Open your browser at: http://localhost:8001
echo.

start "DataSense AI - FastAPI" cmd /k ".venv\Scripts\uvicorn api.app:app --host 127.0.0.1 --port 8001 --reload"

timeout /t 2 /nobreak >nul
start "" "http://localhost:8001"

echo Server is starting — browser will open automatically.
pause
