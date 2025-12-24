@echo off
echo ========================================
echo IoT Security Dashboard - Full Stack
echo ========================================
echo.

echo [INFO] Starting Backend (FastAPI)...
cd backend
start "IoT Backend API" cmd /k "python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 5000"

echo [INFO] Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo [INFO] Starting Frontend (React)...
cd ..\frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo [INFO] Installing frontend dependencies...
    npm install --silent
)

start "IoT Frontend" cmd /k "npm start"

echo.
echo ========================================
echo Full Stack Application Starting!
echo ========================================
echo.
echo Backend API:     http://localhost:5000
echo API Docs:        http://localhost:5000/docs
echo Frontend:        http://localhost:3000
echo Test Interface:  frontend/test.html
echo.
echo [INFO] Both services are starting in separate windows
echo [INFO] Frontend will open automatically in your browser
echo.
echo Press any key to close this window...
pause >nul