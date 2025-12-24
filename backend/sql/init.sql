-- IoT Security Dashboard Database Schema
-- PostgreSQL 15+ with UUID extension

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE device_status AS ENUM ('online', 'offline', 'unknown');
CREATE TYPE alert_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE alert_status AS ENUM ('open', 'investigating', 'resolved', 'false_positive');
CREATE TYPE vulnerability_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE patch_status AS ENUM ('unpatched', 'in_progress', 'patched', 'mitigated');

-- Devices table
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ip_address INET NOT NULL,
    mac_address MACADDR,
    device_type VARCHAR(100),
    vendor VARCHAR(100),
    os_version VARCHAR(100),
    firmware_version VARCHAR(100),
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    risk_score DECIMAL(3,2) DEFAULT 0.0 CHECK (risk_score >= 0 AND risk_score <= 1),
    confidence_score DECIMAL(3,2) DEFAULT 0.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    status device_status DEFAULT 'unknown',
    cve_count INTEGER DEFAULT 0,
    tags JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for devices
CREATE INDEX idx_devices_ip ON devices(ip_address);
CREATE INDEX idx_devices_mac ON devices(mac_address);
CREATE INDEX idx_devices_type ON devices(device_type);
CREATE INDEX idx_devices_vendor ON devices(vendor);
CREATE INDEX idx_devices_risk ON devices(risk_score DESC);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_last_seen ON devices(last_seen DESC);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    severity alert_severity NOT NULL,
    description TEXT NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
    evidence JSONB DEFAULT '{}',
    status alert_status DEFAULT 'open',
    assigned_to VARCHAR(100),
    mitigation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for alerts
CREATE INDEX idx_alerts_device ON alerts(device_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);

-- Vulnerabilities table
CREATE TABLE vulnerabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
    cve_id VARCHAR(50) NOT NULL,
    cvss_score DECIMAL(3,1) CHECK (cvss_score >= 0 AND cvss_score <= 10),
    severity vulnerability_severity NOT NULL,
    description TEXT,
    affected_version VARCHAR(100),
    fixed_version VARCHAR(100),
    exploit_available BOOLEAN DEFAULT FALSE,
    publicly_exploited BOOLEAN DEFAULT FALSE,
    patch_status patch_status DEFAULT 'unpatched',
    discovered_date DATE,
    patch_deadline DATE,
    references JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for vulnerabilities
CREATE INDEX idx_vulns_device ON vulnerabilities(device_id);
CREATE INDEX idx_vulns_cve ON vulnerabilities(cve_id);
CREATE INDEX idx_vulns_severity ON vulnerabilities(severity);
CREATE INDEX idx_vulns_cvss ON vulnerabilities(cvss_score DESC);
CREATE INDEX idx_vulns_patch_status ON vulnerabilities(patch_status);

-- Network flows table
CREATE TABLE network_flows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    source_ip INET NOT NULL,
    destination_ip INET NOT NULL,
    source_port INTEGER,
    destination_port INTEGER,
    protocol VARCHAR(20),
    bytes_sent BIGINT DEFAULT 0,
    bytes_received BIGINT DEFAULT 0,
    packets_sent INTEGER DEFAULT 0,
    packets_received INTEGER DEFAULT 0,
    duration DECIMAL(10,3),
    flags VARCHAR(50),
    anomaly_score DECIMAL(3,2) DEFAULT 0.0 CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    is_anomaly BOOLEAN DEFAULT FALSE,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for network flows
CREATE INDEX idx_flows_device ON network_flows(device_id);
CREATE INDEX idx_flows_timestamp ON network_flows(timestamp DESC);
CREATE INDEX idx_flows_source ON network_flows(source_ip);
CREATE INDEX idx_flows_destination ON network_flows(destination_ip);
CREATE INDEX idx_flows_anomaly ON network_flows(is_anomaly);
CREATE INDEX idx_flows_protocol ON network_flows(protocol);

-- ML models table
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    model_type VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    is_active BOOLEAN DEFAULT FALSE,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    training_samples INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for ML models
CREATE INDEX idx_models_type ON ml_models(model_type);
CREATE INDEX idx_models_active ON ml_models(is_active);

-- Datasets table
CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    file_path VARCHAR(500) NOT NULL,
    size_gb DECIMAL(8,2),
    device_count INTEGER,
    attack_types JSONB DEFAULT '[]',
    processing_status VARCHAR(50) DEFAULT 'pending',
    processed_samples INTEGER DEFAULT 0,
    total_samples INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Experiments table
CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    datasets JSONB DEFAULT '[]',
    models JSONB DEFAULT '[]',
    parameters JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    results JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id)
);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vulnerabilities_updated_at BEFORE UPDATE ON vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ml_models_updated_at BEFORE UPDATE ON ml_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO devices (ip_address, mac_address, device_type, vendor, os_version, status, risk_score, confidence_score) VALUES
('192.168.1.100', '00:1B:44:11:3A:B7', 'Security Camera', 'Hikvision', 'Linux 4.4', 'online', 0.75, 0.92),
('192.168.1.101', '00:1B:44:11:3A:B8', 'Smart Thermostat', 'Nest', 'ThreadOS 2.1', 'online', 0.25, 0.95),
('192.168.1.102', '00:1B:44:11:3A:B9', 'Smart Lock', 'August', 'FreeRTOS 10.2', 'offline', 0.85, 0.88),
('192.168.1.103', '00:1B:44:11:3A:BA', 'Motion Sensor', 'Philips', 'Zigbee 3.0', 'online', 0.15, 0.90),
('192.168.1.104', '00:1B:44:11:3A:BB', 'Smart Hub', 'Samsung', 'Tizen 6.0', 'online', 0.05, 0.98);

-- Insert sample alerts
INSERT INTO alerts (device_id, alert_type, severity, description, confidence, evidence) VALUES
((SELECT id FROM devices WHERE ip_address = '192.168.1.100'), 'Port Scanning', 'HIGH', 'Suspicious port scanning activity detected from external IP', 0.95, '{"source_ip": "203.0.113.1", "ports_scanned": [22, 23, 80, 443, 8080]}'),
((SELECT id FROM devices WHERE ip_address = '192.168.1.102'), 'Firmware Vulnerability', 'CRITICAL', 'Device running firmware with known critical vulnerabilities', 0.98, '{"cve_ids": ["CVE-2023-1234", "CVE-2023-5678"], "exploit_available": true}'),
((SELECT id FROM devices WHERE ip_address = '192.168.1.100'), 'Anomalous Traffic', 'MEDIUM', 'Unusual traffic pattern detected - data exfiltration possible', 0.78, '{"bytes_transferred": 1048576, "destination": "suspicious-domain.com", "protocol": "HTTPS"}}');

-- Insert sample vulnerabilities
INSERT INTO vulnerabilities (device_id, cve_id, cvss_score, severity, description, exploit_available, patch_status) VALUES
((SELECT id FROM devices WHERE ip_address = '192.168.1.100'), 'CVE-2023-1234', 9.8, 'CRITICAL', 'Remote code execution vulnerability in web interface', TRUE, 'unpatched'),
((SELECT id FROM devices WHERE ip_address = '192.168.1.102'), 'CVE-2023-5678', 7.5, 'HIGH', 'Authentication bypass in firmware update mechanism', TRUE, 'unpatched'),
((SELECT id FROM devices WHERE ip_address = '192.168.1.101'), 'CVE-2023-9012', 5.3, 'MEDIUM', 'Information disclosure through debug interface', FALSE, 'patched');

-- Insert sample ML models
INSERT INTO ml_models (name, model_type, version, description, is_active, accuracy, precision_score, recall, f1_score, training_samples) VALUES
('device_fingerprinter_v2', 'device_classification', '2.1.0', 'Random Forest ensemble for device fingerprinting', TRUE, 0.9920, 0.9890, 0.9920, 0.9905, 50000),
('anomaly_detector_v1', 'anomaly_detection', '1.5.0', 'Isolation Forest + LSTM for anomaly detection', TRUE, 0.9670, 0.9450, 0.9670, 0.9558, 75000),
('threat_predictor_v1', 'threat_prediction', '1.2.0', 'XGBoost with SHAP for threat prediction', TRUE, 0.9340, 0.9120, 0.9340, 0.9229, 30000);

-- Insert sample datasets
INSERT INTO datasets (name, description, file_path, size_gb, device_count, attack_types, processing_status, total_samples) VALUES
('TON_IoT', 'Comprehensive IoT security dataset from UNSW', '/datasets/ton_iot/', 500.0, 1452, '["dos", "ddos", "injection", "backdoor", "scanning", "xss", "password", "ransomware", "mitm"]', 'completed', 1500000),
('IoT-23', 'Malware and benign IoT traffic dataset', '/datasets/iot23/', 45.0, 23, '["mirai", "torii", "hajime", "muhstik", "bashlite"]', 'completed', 1000000),
('Edge-IIoTset', 'Industrial IoT security dataset', '/datasets/edge_iiot/', 120.0, 75, '["dos", "ddos", "mitm", "injection", "backdoor"]', 'completed', 1200000),
('BoT-IoT', 'Botnet IoT dataset from UNSW', '/datasets/bot_iot/', 69.0, 6, '["ddos", "dos", "reconnaissance", "theft", "keylogging"]', 'completed', 800000);

-- Create default admin user (password: admin123)
INSERT INTO users (username, email, full_name, hashed_password, role) VALUES
('admin', 'admin@iot-security.local', 'System Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJK9fHPyy', 'admin');

-- Create views for common queries
CREATE VIEW device_summary AS
SELECT 
    d.id,
    d.ip_address,
    d.device_type,
    d.vendor,
    d.status,
    d.risk_score,
    COUNT(DISTINCT a.id) as alert_count,
    COUNT(DISTINCT v.id) as vulnerability_count,
    MAX(a.created_at) as last_alert
FROM devices d
LEFT JOIN alerts a ON d.id = a.device_id AND a.status != 'resolved'
LEFT JOIN vulnerabilities v ON d.id = v.device_id AND v.patch_status != 'patched'
GROUP BY d.id, d.ip_address, d.device_type, d.vendor, d.status, d.risk_score;

CREATE VIEW alert_summary AS
SELECT 
    severity,
    status,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence
FROM alerts
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY severity, status;

-- Grant permissions (adjust as needed for your security requirements)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO iot_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO iot_app_user;