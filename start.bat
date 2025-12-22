@echo off
echo ========================================
echo IoT Security Dashboard Startup Script
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo.
echo Starting IoT Security Dashboard...
echo.

echo [1/4] Setting up backend environment...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1

echo Setting environment variables...
set PYTHONPATH=%cd%\src
set DATABASE_URL=sqlite:///./iot_security.db

echo [2/4] Starting backend server...
start "IoT Backend" cmd /k "uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo [3/4] Setting up frontend...
cd ..\frontend

if not exist node_modules (
    echo Installing Node.js dependencies...
    npm install
)

echo [4/4] Starting frontend server...
start "IoT Frontend" cmd /k "npm start"

echo.
echo ========================================
echo IoT Security Dashboard is starting!
echo ========================================
echo.
echo Backend API:     http://localhost:8000
echo API Docs:        http://localhost:8000/docs
echo Frontend:        http://localhost:3000
echo.
echo The dashboard will open automatically in your browser.
echo Press any key to close this window...
pause >nul