@echo off
echo Starting SQLAgent-Mini-Project...

echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "uvicorn api.app:app --reload --port 8000"

echo Starting Streamlit Frontend...
start "Streamlit Frontend" cmd /k "streamlit run frontend/app.py"

echo Both services are starting in separate windows.
echo You can close this window now.
pause
