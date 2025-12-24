from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
import asyncio

from ..models import (
    DeviceResponse, DeviceCreate, DeviceUpdate, DeviceFingerprint,
    PaginationParams, PaginatedResponse
)
from ...database.session import get_db
from ...database.models import Device, Alert, Vulnerability
from ...detection_engine.fingerprinter import DeviceFingerprinter
from ...utils.logger import setup_logger
from ...utils.metrics import METRICS

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def list_devices(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=1000),
    device_type: Optional[str] = Query(None),
    vendor: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    risk_threshold: Optional[float] = Query(None, ge=0, le=1),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List devices with filtering and pagination"""
    
    # Build query
    query = select(Device)
    count_query = select(func.count(Device.id))
    
    # Apply filters
    filters = []
    
    if device_type:
        filters.append(Device.device_type == device_type)
    
    if vendor:
        filters.append(Device.vendor == vendor)
    
    if status:
        filters.append(Device.status == status)
    
    if risk_threshold is not None:
        filters.append(Device.risk_score >= risk_threshold)
    
    if search:
        search_filter = or_(
            Device.device_type.ilike(f"%{search}%"),
            Device.vendor.ilike(f"%{search}%"),
            Device.ip_address.cast(str).ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Device.last_seen.desc())
    
    # Execute query
    result = await db.execute(query)
    devices = result.scalars().all()
    
    # Update metrics
    METRICS.update_device_count(total)
    
    return PaginatedResponse(
        items=[DeviceResponse.from_orm(device) for device in devices],
        total=total,
        page=page,
        size=size
    )

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get device details by ID"""
    
    query = select(Device).where(Device.id == device_id)
    result = await db.execute(query)
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return DeviceResponse.from_orm(device)

@router.post("/{device_id}/fingerprint", response_model=DeviceFingerprint)
async def fingerprint_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Re-fingerprint a specific device"""
    
    # Get device
    query = select(Device).where(Device.id == device_id)
    result = await db.execute(query)
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    try:
        # Initialize fingerprinter
        fingerprinter = DeviceFingerprinter()
        
        # Mock fingerprinting process (in real implementation, this would analyze network traffic)
        fingerprint_result = await fingerprinter.fingerprint_device(str(device.ip_address))
        
        # Update device with new fingerprint data
        device.device_type = fingerprint_result.get("device_type", device.device_type)
        device.vendor = fingerprint_result.get("vendor", device.vendor)
        device.confidence_score = fingerprint_result.get("confidence", device.confidence_score)
        
        await db.commit()
        
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

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: UUID,
    device_update: DeviceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update device information"""
    
    # Get device
    query = select(Device).where(Device.id == device_id)
    result = await db.execute(query)
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Update fields
    update_data = device_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    
    await db.commit()
    await db.refresh(device)
    
    logger.info(f"Device {device_id} updated")
    
    return DeviceResponse.from_orm(device)

@router.delete("/{device_id}")
async def delete_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a device (admin only)"""
    
    # Get device
    query = select(Device).where(Device.id == device_id)
    result = await db.execute(query)
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Delete device (cascades to related records)
    await db.delete(device)
    await db.commit()
    
    logger.info(f"Device {device_id} deleted")
    
    return {"message": "Device deleted successfully"}

@router.get("/{device_id}/alerts")
async def get_device_alerts(
    device_id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get alerts for a specific device"""
    
    # Verify device exists
    device_query = select(Device).where(Device.id == device_id)
    device_result = await db.execute(device_query)
    device = device_result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get alerts
    offset = (page - 1) * size
    query = (
        select(Alert)
        .where(Alert.device_id == device_id)
        .order_by(Alert.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(Alert.id)).where(Alert.device_id == device_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return PaginatedResponse(
        items=alerts,
        total=total,
        page=page,
        size=size
    )

@router.get("/{device_id}/vulnerabilities")
async def get_device_vulnerabilities(
    device_id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get vulnerabilities for a specific device"""
    
    # Verify device exists
    device_query = select(Device).where(Device.id == device_id)
    device_result = await db.execute(device_query)
    device = device_result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get vulnerabilities
    offset = (page - 1) * size
    query = (
        select(Vulnerability)
        .where(Vulnerability.device_id == device_id)
        .order_by(Vulnerability.cvss_score.desc())
        .offset(offset)
        .limit(size)
    )
    
    result = await db.execute(query)
    vulnerabilities = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(Vulnerability.id)).where(Vulnerability.device_id == device_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return PaginatedResponse(
        items=vulnerabilities,
        total=total,
        page=page,
        size=size
    )

@router.get("/{device_id}/traffic")
async def get_device_traffic(
    device_id: UUID,
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    db: AsyncSession = Depends(get_db)
):
    """Get network traffic patterns for a device"""
    
    # Verify device exists
    device_query = select(Device).where(Device.id == device_id)
    device_result = await db.execute(device_query)
    device = device_result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Mock traffic data (in real implementation, query from InfluxDB or time-series DB)
    import random
    from datetime import datetime, timedelta
    
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
async def scan_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Trigger security scan for a device"""
    
    # Verify device exists
    device_query = select(Device).where(Device.id == device_id)
    device_result = await db.execute(device_query)
    device = device_result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Trigger background scan task
    from ...tasks.device_tasks import scan_device_task
    
    task = scan_device_task.delay(str(device_id))
    
    logger.info(f"Security scan initiated for device {device_id}")
    
    return {
        "message": f"Security scan initiated for device {device_id}",
        "scan_id": task.id,
        "device_id": str(device_id),
        "status": "initiated"
    }