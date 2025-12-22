-- IoT Security Dashboard Database Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Devices table
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    device_type VARCHAR(100) NOT NULL,
    ip_address INET,
    mac_address MACADDR,
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    firmware_version VARCHAR(100),
    status VARCHAR(50) DEFAULT 'unknown',
    security_score INTEGER DEFAULT 0,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Network traffic table
CREATE TABLE network_traffic (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES devices(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    src_ip INET,
    dst_ip INET,
    src_port INTEGER,
    dst_port INTEGER,
    protocol VARCHAR(10),
    packet_size INTEGER,
    flags VARCHAR(50),
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_score FLOAT DEFAULT 0.0
);

-- Vulnerabilities table
CREATE TABLE vulnerabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES devices(id),
    cve_id VARCHAR(50),
    severity VARCHAR(20),
    description TEXT,
    cvss_score FLOAT,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'open'
);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES devices(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metadata JSONB,
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- ML Models table
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    accuracy FLOAT,
    precision_score FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_last_seen ON devices(last_seen);
CREATE INDEX idx_network_traffic_timestamp ON network_traffic(timestamp);
CREATE INDEX idx_network_traffic_device_id ON network_traffic(device_id);
CREATE INDEX idx_vulnerabilities_device_id ON vulnerabilities(device_id);
CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX idx_alerts_device_id ON alerts(device_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);

-- Insert sample data
INSERT INTO devices (name, device_type, ip_address, mac_address, manufacturer, model, status, security_score) VALUES
('Smart Thermostat', 'thermostat', '192.168.1.100', '00:1B:44:11:3A:B7', 'Nest', 'Learning Thermostat', 'online', 85),
('Security Camera', 'camera', '192.168.1.101', '00:1B:44:11:3A:B8', 'Ring', 'Doorbell Pro', 'online', 92),
('Smart Lock', 'lock', '192.168.1.102', '00:1B:44:11:3A:B9', 'August', 'Smart Lock Pro', 'offline', 78),
('Motion Sensor', 'sensor', '192.168.1.103', '00:1B:44:11:3A:BA', 'Philips', 'Hue Motion', 'online', 88),
('Smart Hub', 'hub', '192.168.1.104', '00:1B:44:11:3A:BB', 'Samsung', 'SmartThings Hub', 'online', 95);