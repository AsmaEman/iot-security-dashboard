from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, INET, MACADDR
from datetime import datetime
import uuid

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ip_address = Column(INET, nullable=False)
    mac_address = Column(MACADDR, nullable=True)
    device_type = Column(String(100), nullable=True)
    vendor = Column(String(100), nullable=True)
    os_version = Column(String(100), nullable=True)
    firmware_version = Column(String(100), nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    status = Column(String(20), default='unknown')
    cve_count = Column(Integer, default=0)
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="device", cascade="all, delete-orphan")
    network_flows = relationship("NetworkFlow", back_populates="device", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_devices_ip', 'ip_address'),
        Index('idx_devices_mac', 'mac_address'),
        Index('idx_devices_type', 'device_type'),
        Index('idx_devices_risk', 'risk_score'),
        Index('idx_devices_status', 'status'),
    )

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    confidence = Column(Float, default=0.8)
    evidence = Column(JSON, default=dict)
    status = Column(String(20), default='open')
    assigned_to = Column(String(100), nullable=True)
    mitigation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    device = relationship("Device", back_populates="alerts")
    
    # Indexes
    __table_args__ = (
        Index('idx_alerts_device', 'device_id'),
        Index('idx_alerts_severity', 'severity'),
        Index('idx_alerts_status', 'status'),
        Index('idx_alerts_created', 'created_at'),
    )

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    cve_id = Column(String(50), nullable=False)
    cvss_score = Column(Float, nullable=True)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    affected_version = Column(String(100), nullable=True)
    fixed_version = Column(String(100), nullable=True)
    exploit_available = Column(Boolean, default=False)
    publicly_exploited = Column(Boolean, default=False)
    patch_status = Column(String(20), default='unpatched')
    discovered_date = Column(DateTime, nullable=True)
    patch_deadline = Column(DateTime, nullable=True)
    references = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    device = relationship("Device", back_populates="vulnerabilities")
    
    # Indexes
    __table_args__ = (
        Index('idx_vulns_device', 'device_id'),
        Index('idx_vulns_cve', 'cve_id'),
        Index('idx_vulns_severity', 'severity'),
        Index('idx_vulns_cvss', 'cvss_score'),
    )

class NetworkFlow(Base):
    __tablename__ = "network_flows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    source_ip = Column(INET, nullable=False)
    destination_ip = Column(INET, nullable=False)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    protocol = Column(String(20), nullable=True)
    bytes_sent = Column(Integer, default=0)
    bytes_received = Column(Integer, default=0)
    packets_sent = Column(Integer, default=0)
    packets_received = Column(Integer, default=0)
    duration = Column(Float, nullable=True)
    flags = Column(String(50), nullable=True)
    anomaly_score = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    device = relationship("Device", back_populates="network_flows")
    
    # Indexes
    __table_args__ = (
        Index('idx_flows_device', 'device_id'),
        Index('idx_flows_timestamp', 'timestamp'),
        Index('idx_flows_source', 'source_ip'),
        Index('idx_flows_destination', 'destination_ip'),
        Index('idx_flows_anomaly', 'is_anomaly'),
    )

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    model_type = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    training_samples = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    size_gb = Column(Float, nullable=True)
    device_count = Column(Integer, nullable=True)
    attack_types = Column(JSON, default=list)
    processing_status = Column(String(50), default='pending')
    processed_samples = Column(Integer, default=0)
    total_samples = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default='viewer')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Experiment(Base):
    __tablename__ = "experiments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    datasets = Column(JSON, default=list)
    models = Column(JSON, default=list)
    parameters = Column(JSON, default=dict)
    status = Column(String(50), default='pending')
    results = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)