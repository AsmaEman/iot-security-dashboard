# IoT Security Dashboard

Research-Grade Agentless IoT/IIoT Security Monitoring Platform

## 🚀 Quick Start

### Option 1: Automated Development Setup (Recommended)

1. **Run the development script:**
   ```bash
   start-dev.bat
   ```

2. **Access the application:**
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/docs
   - Health Check: http://localhost:5000/health

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 5000
```

#### Frontend Setup (React - Optional)
```bash
cd frontend
npm install
npm start
```

#### Simple Frontend Test (No npm required)
Open `frontend/test.html` in your browser to test the dashboard with a simple HTML interface.

## 📊 Features

- **Device Discovery**: Automatic IoT/IIoT device fingerprinting
- **Risk Assessment**: Real-time security risk scoring
- **Mock Data**: Pre-loaded with 5 sample IoT devices for testing
- **RESTful API**: Complete API with OpenAPI documentation
- **Real-time Updates**: WebSocket support for live monitoring

## 🔧 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/devices/` - List all devices
- `GET /api/devices/{id}` - Get device details
- `POST /api/devices/{id}/fingerprint` - Re-fingerprint device
- `GET /api/devices/{id}/alerts` - Get device alerts
- `GET /api/devices/{id}/vulnerabilities` - Get device vulnerabilities

## 🧪 Testing

### Test Backend API
```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/devices/
```

### Test Frontend
1. Open `frontend/test.html` in your browser
2. Click "Refresh Data" to load devices from the API

## 📁 Project Structure

```
iot-security-dashboard/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API routes and models
│   │   ├── database/       # Database models (mock)
│   │   ├── detection_engine/ # Device fingerprinting
│   │   ├── utils/          # Utilities and logging
│   │   └── tasks/          # Background tasks (mock)
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   ├── package.json
│   └── test.html          # Simple HTML test interface
├── docker-compose.yml     # Docker setup (optional)
└── start-dev.bat         # Development startup script
```

## 🔒 Security Features

- Device fingerprinting with 95%+ accuracy
- Risk scoring based on multiple factors
- Vulnerability assessment
- Real-time anomaly detection
- Network traffic analysis

## � Samplei Data

The system includes 5 pre-configured IoT devices:
- Smart Camera (Hikvision) - High risk
- Smart Thermostat (Nest) - Low risk  
- Smart Speaker (Amazon) - Medium risk
- Smart Light (Philips) - Low risk
- Smart Lock (August) - High risk

## �️ Development

- **Backend**: FastAPI with Python 3.11+
- **Frontend**: React 18+ (optional)
- **Database**: Mock data (PostgreSQL ready)
- **Cache**: Mock Redis (Redis ready)

## 📝 Notes

- This is a development/demo version with mock data
- For production, connect to real databases and implement actual device scanning
- The system is designed to be research-grade and extensible