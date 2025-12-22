from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional
import json
from datetime import datetime, timedelta

from .models import DeviceResponse, AlertResponse, VulnerabilityResponse, NetworkTrafficResponse
from .dependencies import get_database
from ..detection.fingerprinter import DeviceFingerprinter
from ..detection.anomaly_detector import AnomalyDetector
from ..utils.cache import get_cache

router = APIRouter()

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - can be extended for real-time updates
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/devices", response_model=List[DeviceResponse])
async def get_devices(
    status: Optional[str] = None,
    device_type: Optional[str] = None,
    db = Depends(get_database)
):
    """Get all IoT devices with optional filtering"""
    query = "SELECT * FROM devices WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    if device_type:
        query += " AND device_type = %s"
        params.append(device_type)
    
    query += " ORDER BY last_seen DESC"
    
    # This would be actual database query in real implementation
    devices = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Smart Thermostat",
            "device_type": "thermostat",
            "ip_address": "192.168.1.100",
            "mac_address": "00:1B:44:11:3A:B7",
            "manufacturer": "Nest",
            "model": "Learning Thermostat",
            "firmware_version": "5.9.3",
            "status": "online",
            "security_score": 85,
            "last_seen": datetime.now(),
            "created_at": datetime.now() - timedelta(days=30)
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "name": "Security Camera",
            "device_type": "camera",
            "ip_address": "192.168.1.101",
            "mac_address": "00:1B:44:11:3A:B8",
            "manufacturer": "Ring",
            "model": "Doorbell Pro",
            "firmware_version": "1.4.26",
            "status": "online",
            "security_score": 92,
            "last_seen": datetime.now(),
            "created_at": datetime.now() - timedelta(days=25)
        }
    ]
    
    return devices

@router.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db = Depends(get_database)):
    """Get specific device details"""
    # Mock response - would query database in real implementation
    device = {
        "id": device_id,
        "name": "Smart Thermostat",
        "device_type": "thermostat",
        "ip_address": "192.168.1.100",
        "mac_address": "00:1B:44:11:3A:B7",
        "manufacturer": "Nest",
        "model": "Learning Thermostat",
        "firmware_version": "5.9.3",
        "status": "online",
        "security_score": 85,
        "last_seen": datetime.now(),
        "created_at": datetime.now() - timedelta(days=30)
    }
    
    return device

@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """Get security alerts"""
    alerts = [
        {
            "id": "alert-001",
            "device_id": "550e8400-e29b-41d4-a716-446655440001",
            "alert_type": "suspicious_traffic",
            "severity": "medium",
            "title": "Unusual Network Activity Detected",
            "description": "Device showing abnormal traffic patterns",
            "status": "open",
            "created_at": datetime.now() - timedelta(hours=2)
        },
        {
            "id": "alert-002",
            "device_id": "550e8400-e29b-41d4-a716-446655440002",
            "alert_type": "firmware_vulnerability",
            "severity": "high",
            "title": "Outdated Firmware Detected",
            "description": "Device running firmware with known vulnerabilities",
            "status": "open",
            "created_at": datetime.now() - timedelta(hours=6)
        }
    ]
    
    return alerts

@router.get("/vulnerabilities", response_model=List[VulnerabilityResponse])
async def get_vulnerabilities(device_id: Optional[str] = None):
    """Get device vulnerabilities"""
    vulnerabilities = [
        {
            "id": "vuln-001",
            "device_id": "550e8400-e29b-41d4-a716-446655440002",
            "cve_id": "CVE-2023-1234",
            "severity": "high",
            "description": "Buffer overflow in firmware update mechanism",
            "cvss_score": 8.5,
            "discovered_at": datetime.now() - timedelta(days=1),
            "status": "open"
        }
    ]
    
    return vulnerabilities

@router.get("/network-traffic")
async def get_network_traffic(
    device_id: Optional[str] = None,
    hours: int = 24
):
    """Get network traffic data"""
    # Mock data - would query actual traffic logs
    traffic_data = {
        "total_packets": 15420,
        "anomalous_packets": 23,
        "top_protocols": [
            {"protocol": "HTTPS", "count": 8500},
            {"protocol": "DNS", "count": 3200},
            {"protocol": "MQTT", "count": 2100},
            {"protocol": "HTTP", "count": 1620}
        ],
        "timeline": [
            {"timestamp": datetime.now() - timedelta(hours=i), "packet_count": 640 + (i * 10)}
            for i in range(24, 0, -1)
        ]
    }
    
    return traffic_data

@router.post("/devices/{device_id}/scan")
async def scan_device(device_id: str):
    """Trigger security scan for specific device"""
    # This would trigger actual scanning in real implementation
    return {
        "message": f"Security scan initiated for device {device_id}",
        "scan_id": f"scan-{device_id}-{int(datetime.now().timestamp())}"
    }

@router.get("/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard overview metrics"""
    return {
        "total_devices": 5,
        "online_devices": 4,
        "offline_devices": 1,
        "average_security_score": 87.6,
        "active_alerts": 3,
        "critical_vulnerabilities": 1,
        "network_anomalies_24h": 23,
        "last_updated": datetime.now()
    }