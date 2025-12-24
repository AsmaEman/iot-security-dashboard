from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import uuid

# Base models
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(50, ge=1, le=1000)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int

# Device models
class DeviceBase(BaseModel):
    device_type: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    status: str = "active"
    risk_score: float = 0.0
    confidence_score: float = 0.0

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    device_type: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    status: Optional[str] = None
    risk_score: Optional[float] = None

class DeviceResponse(DeviceBase):
    id: UUID
    first_seen: datetime
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeviceFingerprint(BaseModel):
    device_id: UUID
    dhcp_fingerprint: Optional[Dict[str, Any]] = None
    tls_fingerprint: Optional[Dict[str, Any]] = None
    http_fingerprint: Optional[Dict[str, Any]] = None
    behavioral_fingerprint: Optional[Dict[str, Any]] = None
    confidence: float
    contributing_factors: Dict[str, Any] = {}

# Alert models
class AlertBase(BaseModel):
    title: str
    description: str
    severity: str = "medium"
    alert_type: str = "anomaly"
    status: str = "open"

class AlertResponse(AlertBase):
    id: UUID
    device_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Vulnerability models
class VulnerabilityBase(BaseModel):
    cve_id: str
    title: str
    description: str
    cvss_score: float
    severity: str
    status: str = "open"

class VulnerabilityResponse(VulnerabilityBase):
    id: UUID
    device_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True