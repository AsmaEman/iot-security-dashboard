from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID, uuid4
import asyncio
from datetime import datetime, timedelta
import random

from ..models import (
    DeviceResponse, DeviceCreate, DeviceUpdate, DeviceFingerprint,
    PaginationParams, PaginatedResponse
)
from ...detection_engine.fingerprinter import DeviceFingerprinter
from ...utils.logger import setup_logger
from ...utils.metrics import METRICS

logger = setup_logger(__name__)
router = APIRouter()

# Mock device data for development
MOCK_DEVICES = [
    {
        "id": uuid4(),
        "device_type": "Smart Camera",
        "vendor": "Hikvision",
        "model": "DS-2CD2143G0-I",
        "firmware_version": "V5.6.3",
        "ip_address": "192.168.1.100",
        "mac_address": "00:11:22:33:44:55",
        "status": "active",
        "risk_score": 0.3,
        "confidence_score": 0.95,
        "first_seen": datetime.utcnow() - timedelta(days=30),
        "last_seen": datetime.utcnow() - timedelta(minutes=5),
        "created_at": datetime.utcnow() - timedelta(days=30),
        "updated_at": datetime.utcnow() - timedelta(minutes=5)
    },
    {
        "id": uuid4(),
        "device_type": "Smart Thermostat",
        "vendor": "Nest",
        "model": "Learning Thermostat",
        "firmware_version": "6.0.1",
        "ip_address": "192.168.1.101",
        "mac_address": "00:11:22:33:44:56",
        "status": "active",
        "risk_score": 0.1,
        "confidence_score": 0.92,
        "first_seen": datetime.utcnow() - timedelta(days=15),
        "last_seen": datetime.utcnow() - timedelta(minutes=2),
        "created_at": datetime.utcnow() - timedelta(days=15),
        "updated_at": datetime.utcnow() - timedelta(minutes=2)
    },
    {
        "id": uuid4(),
        "device_type": "Smart Speaker",
        "vendor": "Amazon",
        "model": "Echo Dot",
        "firmware_version": "4.0.2",
        "ip_address": "192.168.1.102",
        "mac_address": "00:11:22:33:44:57",
        "status": "active",
        "risk_score": 0.2,
        "confidence_score": 0.88,
        "first_seen": datetime.utcnow() - timedelta(days=7),
        "last_seen": datetime.utcnow() - timedelta(minutes=1),
        "created_at": datetime.utcnow() - timedelta(days=7),
        "updated_at": datetime.utcnow() - timedelta(minutes=1)
    },
    {
        "id": uuid4(),
        "device_type": "Smart Light",
        "vendor": "Philips",
        "model": "Hue Bulb",
        "firmware_version": "1.50.2",
        "ip_address": "192.168.1.103",
        "mac_address": "00:11:22:33:44:58",
        "status": "active",
        "risk_score": 0.05,
        "confidence_score": 0.85,
        "first_seen": datetime.utcnow() - timedelta(days=3),
        "last_seen": datetime.utcnow() - timedelta(seconds=30),
        "created_at": datetime.utcnow() - timedelta(days=3),
        "updated_at": datetime.utcnow() - timedelta(seconds=30)
    },
    {
        "id": uuid4(),
        "device_type": "Smart Lock",
        "vendor": "August",
        "model": "Smart Lock Pro",
        "firmware_version": "2.1.0",
        "ip_address": "192.168.1.104",
        "mac_address": "00:11:22:33:44:59",
        "status": "active",
        "risk_score": 0.4,
        "confidence_score": 0.90,
        "first_seen": datetime.utcnow() - timedelta(days=1),
        "last_seen": datetime.utcnow() - timedelta(minutes=10),
        "created_at": datetime.utcnow() - timedelta(days=1),
        "updated_at": datetime.utcnow() - timedelta(minutes=10)
    }
]

@router.get("/", response_model=PaginatedResponse)
async def list_devices(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=1000),
    device_type: Optional[str] = Query(None),
    vendor: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    risk_threshold: Optional[float] = Query(None, ge=0, le=1),
    search: Optional[str] = Query(None)
):
    """List devices with filtering and pagination"""
    
    # Filter devices based on query parameters
    filtered_devices = MOCK_DEVICES.copy()
    
    if device_type:
        filtered_devices = [d for d in filtered_devices if d["device_type"] == device_type]
    
    if vendor:
        filtered_devices = [d for d in filtered_devices if d["vendor"] == vendor]
    
    if status:
        filtered_devices = [d for d in filtered_devices if d["status"] == status]
    
    if risk_threshold is not None:
        filtered_devices = [d for d in filtered_devices if d["risk_score"] >= risk_threshold]
    
    if search:
        search_lower = search.lower()
        filtered_devices = [
            d for d in filtered_devices 
            if search_lower in d["device_type"].lower() 
            or search_lower in d["vendor"].lower()
            or search_lower in d["ip_address"]
        ]
    
    total = len(filtered_devices)
    
    # Apply pagination
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_devices = filtered_devices[start_idx:end_idx]
    
    # Update metrics
    METRICS.update_device_count(total)
    
    return PaginatedResponse(
        items=paginated_devices,
        total=total,
        page=page,
        size=size
    )

@router.get("/{device_id}")
async def get_device(device_id: UUID):
    """Get device details by ID"""
    
    device = next((d for d in MOCK_DEVICES if d["id"] == device_id), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return device

@router.post("/{device_id}/fingerprint", response_model=DeviceFingerprint)
async def fingerprint_device(device_id: UUID):
    """Re-fingerprint a specific device"""
    
    device = next((d for d in MOCK_DEVICES if d["id"] == device_id), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    try:
        # Initialize fingerprinter
        fingerprinter = DeviceFingerprinter()
        
        # Mock fingerprinting process
        fingerprint_result = await fingerprinter.fingerprint_device(device["ip_address"])
        
        # Record metrics
        METRICS.record_device_identification(
            fingerprint_result.get("confidence", 0.0),
            fingerprint_result.get("processing_time", 0.0)
        )
        
        return DeviceFingerprint(
            device_id=device_id,
            dhcp_fingerprint=fingerprint_result.get("dhcp_fingerprint"),
            tls_fingerprint=fingerprint_result.get("tls_fingerprint"),
            http_fingerprint=fingerprint_result.get("http_fingerprint"),
            behavioral_fingerprint=fingerprint_result.get("behavioral_fingerprint"),
            confidence=fingerprint_result.get("confidence", 0.0),
            contributing_factors=fingerprint_result.get("contributing_factors", {})
        )
        
    except Exception as e:
        logger.error(f"Fingerprinting failed for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Fingerprinting failed")

@router.get("/{device_id}/alerts")
async def get_device_alerts(
    device_id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=1000)
):
    """Get alerts for a specific device"""
    
    device = next((d for d in MOCK_DEVICES if d["id"] == device_id), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Mock alerts data
    mock_alerts = [
        {
            "id": uuid4(),
            "device_id": device_id,
            "title": "Unusual Network Activity",
            "description": "Device showing abnormal traffic patterns",
            "severity": "medium",
            "alert_type": "anomaly",
            "status": "open",
            "created_at": datetime.utcnow() - timedelta(hours=2),
            "updated_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "id": uuid4(),
            "device_id": device_id,
            "title": "Firmware Vulnerability",
            "description": "Outdated firmware version detected",
            "severity": "high",
            "alert_type": "vulnerability",
            "status": "open",
            "created_at": datetime.utcnow() - timedelta(days=1),
            "updated_at": datetime.utcnow() - timedelta(days=1)
        }
    ]
    
    total = len(mock_alerts)
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_alerts = mock_alerts[start_idx:end_idx]
    
    return PaginatedResponse(
        items=paginated_alerts,
        total=total,
        page=page,
        size=size
    )

@router.get("/{device_id}/vulnerabilities")
async def get_device_vulnerabilities(
    device_id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=1000)
):
    """Get vulnerabilities for a specific device"""
    
    device = next((d for d in MOCK_DEVICES if d["id"] == device_id), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Mock vulnerabilities data
    mock_vulnerabilities = [
        {
            "id": uuid4(),
            "device_id": device_id,
            "cve_id": "CVE-2023-1234",
            "title": "Buffer Overflow in Web Interface",
            "description": "A buffer overflow vulnerability exists in the web management interface",
            "cvss_score": 7.5,
            "severity": "high",
            "status": "open",
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(days=5)
        },
        {
            "id": uuid4(),
            "device_id": device_id,
            "cve_id": "CVE-2023-5678",
            "title": "Weak Default Credentials",
            "description": "Device uses weak default credentials",
            "cvss_score": 5.3,
            "severity": "medium",
            "status": "open",
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow() - timedelta(days=10)
        }
    ]
    
    total = len(mock_vulnerabilities)
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_vulns = mock_vulnerabilities[start_idx:end_idx]
    
    return PaginatedResponse(
        items=paginated_vulns,
        total=total,
        page=page,
        size=size
    )

@router.get("/{device_id}/traffic")
async def get_device_traffic(
    device_id: UUID,
    hours: int = Query(24, ge=1, le=168)  # 1 hour to 1 week
):
    """Get network traffic patterns for a device"""
    
    device = next((d for d in MOCK_DEVICES if d["id"] == device_id), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Mock traffic data
    traffic_data = {
        "device_id": str(device_id),
        "time_range_hours": hours,
        "total_bytes": random.randint(1000000, 10000000),
        "total_packets": random.randint(10000, 100000),
        "unique_destinations": random.randint(10, 100),
        "protocols": {
            "TCP": random.randint(60, 80),
            "UDP": random.randint(15, 25),
            "ICMP": random.randint(1, 5)
        },
        "hourly_stats": [
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "bytes": random.randint(10000, 100000),
                "packets": random.randint(100, 1000),
                "anomaly_score": random.uniform(0, 0.3)
            }
            for i in range(hours, 0, -1)
        ]
    }
    
    return traffic_data

@router.post("/{device_id}/scan")
async def scan_device(device_id: UUID):
    """Trigger security scan for a device"""
    
    device = next((d for d in MOCK_DEVICES if d["id"] == device_id), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Mock scan task
    from ...tasks.device_tasks import scan_device_task
    
    task = scan_device_task.delay(str(device_id))
    
    logger.info(f"Security scan initiated for device {device_id}")
    
    return {
        "message": f"Security scan initiated for device {device_id}",
        "scan_id": task.id,
        "device_id": str(device_id),
        "status": "initiated"
    }