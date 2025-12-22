#!/bin/bash

echo "========================================"
echo "IoT Security Dashboard Startup Script"
echo "========================================"
echo

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

echo "Starting IoT Security Dashboard..."
echo

echo "[1/4] Setting up backend environment..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "Setting environment variables..."
export PYTHONPATH=$(pwd)/src
export DATABASE_URL="sqlite:///./iot_security.db"

echo "[2/4] Starting backend server..."
gnome-terminal -- bash -c "uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000; exec bash" 2>/dev/null || \
xterm -e "uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000" 2>/dev/null || \
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &

echo "Waiting for backend to start..."
sleep 5

echo "[3/4] Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "[4/4] Starting frontend server..."
gnome-terminal -- bash -c "npm start; exec bash" 2>/dev/null || \
xterm -e "npm start" 2>/dev/null || \
npm start &

echo
echo "========================================"
echo "IoT Security Dashboard is starting!"
echo "========================================"
echo
echo "Backend API:     http://localhost:8000"
echo "API Docs:        http://localhost:8000/docs"
echo "Frontend:        http://localhost:3000"
echo
echo "The dashboard will open automatically in your browser."
echo "Press Ctrl+C to stop all services."

# Keep script running
wait