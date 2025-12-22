from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class DeviceBase(BaseModel):
    name: str
    device_type: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: str
    status: str
    security_score: int
    last_seen: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    device_id: str
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VulnerabilityBase(BaseModel):
    device_id: str
    cve_id: Optional[str] = None
    severity: str
    description: str
    cvss_score: Optional[float] = None

class VulnerabilityCreate(VulnerabilityBase):
    pass

class VulnerabilityResponse(VulnerabilityBase):
    id: str
    discovered_at: datetime
    status: str

    class Config:
        from_attributes = True

class NetworkTrafficBase(BaseModel):
    device_id: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    packet_size: Optional[int] = None

class NetworkTrafficCreate(NetworkTrafficBase):
    pass

class NetworkTrafficResponse(NetworkTrafficBase):
    id: str
    timestamp: datetime
    is_anomaly: bool
    anomaly_score: float

    class Config:
        from_attributes = True

class MLModelBase(BaseModel):
    name: str
    model_type: str
    version: str
    file_path: Optional[str] = None

class MLModelCreate(MLModelBase):
    pass

class MLModelResponse(MLModelBase):
    id: str
    accuracy: Optional[float] = None
    precision_score: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ScanRequest(BaseModel):
    device_id: str
    scan_type: str = Field(default="full", description="Type of scan: quick, full, or deep")
    
class ScanResponse(BaseModel):
    scan_id: str
    device_id: str
    status: str
    started_at: datetime
    estimated_completion: Optional[datetime] = None