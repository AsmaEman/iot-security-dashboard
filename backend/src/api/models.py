from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

# Enums
class DeviceStatus(str, Enum):
    online = "online"
    offline = "offline"
    unknown = "unknown"

class AlertSeverity(str, Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"

class AlertStatus(str, Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"
    false_positive = "false_positive"

class VulnerabilitySeverity(str, Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"

class PatchStatus(str, Enum):
    unpatched = "unpatched"
    in_progress = "in_progress"
    patched = "patched"
    mitigated = "mitigated"

# Base Models
class TimestampMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Device Models
class DeviceBase(BaseModel):
    ip_address: str = Field(..., description="Device IP address")
    mac_address: Optional[str] = Field(None, description="Device MAC address")
    device_type: Optional[str] = Field(None, description="Type of device (e.g., Security Camera)")
    vendor: Optional[str] = Field(None, description="Device vendor/manufacturer")
    os_version: Optional[str] = Field(None, description="Operating system version")
    firmware_version: Optional[str] = Field(None, description="Firmware version")
    status: DeviceStatus = Field(default=DeviceStatus.unknown)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    device_type: Optional[str] = None
    vendor: Optional[str] = None
    os_version: Optional[str] = None
    firmware_version: Optional[str] = None
    status: Optional[DeviceStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class DeviceResponse(DeviceBase, TimestampMixin):
    id: UUID
    first_seen: datetime
    last_seen: datetime
    risk_score: float = Field(ge=0, le=1, description="Risk score from 0 to 1")
    confidence_score: float = Field(ge=0, le=1, description="Identification confidence")
    cve_count: int = Field(ge=0, description="Number of CVEs affecting this device")

    class Config:
        from_attributes = True

class DeviceFingerprint(BaseModel):
    device_id: UUID
    dhcp_fingerprint: Optional[Dict[str, Any]] = None
    tls_fingerprint: Optional[Dict[str, Any]] = None
    http_fingerprint: Optional[Dict[str, Any]] = None
    behavioral_fingerprint: Optional[Dict[str, Any]] = None
    confidence: float = Field(ge=0, le=1)
    contributing_factors: Dict[str, float]

# Alert Models
class AlertBase(BaseModel):
    device_id: UUID
    alert_type: str = Field(..., description="Type of alert (e.g., Port Scanning)")
    severity: AlertSeverity
    description: str = Field(..., description="Alert description")
    confidence: float = Field(default=0.8, ge=0, le=1)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    status: AlertStatus = Field(default=AlertStatus.open)
    assigned_to: Optional[str] = None
    mitigation: Optional[str] = None

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to: Optional[str] = None
    mitigation: Optional[str] = None

class AlertResponse(AlertBase, TimestampMixin):
    id: UUID
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AlertStats(BaseModel):
    total_alerts: int
    open_alerts: int
    resolved_alerts: int
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    recent_alerts: List[AlertResponse]

# Vulnerability Models
class VulnerabilityBase(BaseModel):
    device_id: UUID
    cve_id: str = Field(..., description="CVE identifier")
    cvss_score: Optional[float] = Field(None, ge=0, le=10)
    severity: VulnerabilitySeverity
    description: Optional[str] = None
    affected_version: Optional[str] = None
    fixed_version: Optional[str] = None
    exploit_available: bool = Field(default=False)
    publicly_exploited: bool = Field(default=False)
    patch_status: PatchStatus = Field(default=PatchStatus.unpatched)
    discovered_date: Optional[datetime] = None
    patch_deadline: Optional[datetime] = None
    references: List[str] = Field(default_factory=list)

class VulnerabilityCreate(VulnerabilityBase):
    pass

class VulnerabilityUpdate(BaseModel):
    patch_status: Optional[PatchStatus] = None
    patch_deadline: Optional[datetime] = None

class VulnerabilityResponse(VulnerabilityBase, TimestampMixin):
    id: UUID

    class Config:
        from_attributes = True

# Network Flow Models
class NetworkFlowBase(BaseModel):
    device_id: UUID
    timestamp: datetime
    source_ip: str
    destination_ip: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    bytes_sent: int = Field(default=0, ge=0)
    bytes_received: int = Field(default=0, ge=0)
    packets_sent: int = Field(default=0, ge=0)
    packets_received: int = Field(default=0, ge=0)
    duration: Optional[float] = None
    flags: Optional[str] = None
    anomaly_score: float = Field(default=0.0, ge=0, le=1)
    is_anomaly: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)

class NetworkFlowCreate(NetworkFlowBase):
    pass

class NetworkFlowResponse(NetworkFlowBase, TimestampMixin):
    id: UUID

    class Config:
        from_attributes = True

# ML Model Models
class MLModelBase(BaseModel):
    name: str
    model_type: str = Field(..., description="Type of model (e.g., device_classifier)")
    version: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    is_active: bool = Field(default=False)

class MLModelCreate(MLModelBase):
    pass

class MLModelResponse(MLModelBase, TimestampMixin):
    id: UUID
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    training_samples: Optional[int] = None

    class Config:
        from_attributes = True

class MLPredictionRequest(BaseModel):
    model_name: str
    features: Dict[str, Any]

class MLPredictionResponse(BaseModel):
    prediction: Any
    confidence: float
    model_version: str
    inference_time_ms: float

# Dataset Models
class DatasetBase(BaseModel):
    name: str = Field(..., description="Dataset name (e.g., TON_IoT)")
    description: Optional[str] = None
    file_path: str
    size_gb: Optional[float] = None
    device_count: Optional[int] = None
    attack_types: List[str] = Field(default_factory=list)

class DatasetCreate(DatasetBase):
    pass

class DatasetResponse(DatasetBase, TimestampMixin):
    id: UUID
    processing_status: str = Field(default="pending")
    processed_samples: int = Field(default=0)
    total_samples: Optional[int] = None

    class Config:
        from_attributes = True

class DatasetProcessingRequest(BaseModel):
    dataset_name: str
    processing_options: Dict[str, Any] = Field(default_factory=dict)

class DatasetMetrics(BaseModel):
    dataset_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: List[List[int]]
    roc_auc: Optional[float] = None

# Research Models
class ResearchMetrics(BaseModel):
    total_datasets: int
    total_devices: int
    total_samples: int
    model_performance: Dict[str, Dict[str, float]]
    comparative_analysis: Dict[str, Dict[str, float]]

class ExperimentRequest(BaseModel):
    experiment_name: str
    datasets: List[str]
    models: List[str]
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ExperimentResponse(BaseModel):
    experiment_id: UUID
    status: str
    results: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

# Authentication Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: Optional[str] = None
    role: str = Field(default="viewer")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase, TimestampMixin):
    id: UUID
    is_active: bool = Field(default=True)

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[UUID] = None
    role: Optional[str] = None

# Dashboard Models
class DashboardMetrics(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    high_risk_devices: int
    active_alerts: int
    critical_vulnerabilities: int
    network_anomalies_24h: int
    average_risk_score: float
    last_updated: datetime

class TopologyNode(BaseModel):
    id: str
    label: str
    device_type: str
    risk_score: float
    status: str
    x: Optional[float] = None
    y: Optional[float] = None

class TopologyEdge(BaseModel):
    source: str
    target: str
    weight: float
    protocol: str
    bytes_transferred: int

class NetworkTopology(BaseModel):
    nodes: List[TopologyNode]
    edges: List[TopologyEdge]
    last_updated: datetime

# Pagination Models
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=1000)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

    @validator('pages', always=True)
    def calculate_pages(cls, v, values):
        total = values.get('total', 0)
        size = values.get('size', 50)
        return (total + size - 1) // size if total > 0 else 0