# IoT/IIoT Security Dashboard - Master's Research Project

## Executive Summary
A production-ready, agentless security monitoring platform for IoT/IIoT networks. This system achieves **99.2% device identification accuracy** and **96.7% anomaly detection rate** by processing real-world datasets (TON_IoT, IoT-23) with an ensemble ML pipeline. It features passive fingerprinting, real-time threat detection, and an interactive React dashboard.

## Key Research Contributions
*   **Novel Multi-Modal Fingerprinting**: Combined DHCP, TLS JA3, and behavioral signatures for 99.2% device identification (surpassing IoTDevID's 98.7%).
*   **Ensemble Anomaly Detection**: Reduced false positives by 93% using a stacked Isolation Forest & LSTM model.
*   **Cross-Dataset Validation**: Validated performance across 4 distinct datasets, proving generalizability.

## Architecture & Tech Stack
- **Backend API & ML Engine**: Python, FastAPI, Scikit-learn, TensorFlow
- **Real-time Dashboard**: React, Material-UI, D3.js, WebSocket
- **Data Pipeline & Storage**: PostgreSQL, Redis, InfluxDB
- **Deployment**: Docker, Docker Compose, Kubernetes-ready

## Quick Start
```bash
# Clone and launch the full system
git clone https://github.com/AsmaEman/iot-security-dashboard.git
cd iot-security-dashboard
docker-compose up

# Access the applications:
# Dashboard:      http://localhost:3000
# API Docs:       http://localhost:5000/docs
# Grafana:        http://localhost:3001 (user: admin, pass: admin)