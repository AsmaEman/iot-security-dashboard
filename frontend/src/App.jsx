import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/devices/');
      setDevices(response.data.items || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch devices: ' + err.message);
      console.error('Error fetching devices:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getRiskColor = (riskScore) => {
    if (riskScore >= 0.7) return '#ff4757';
    if (riskScore >= 0.4) return '#ffa502';
    if (riskScore >= 0.2) return '#ffb142';
    return '#2ed573';
  };

  const getRiskLevel = (riskScore) => {
    if (riskScore >= 0.7) return 'Critical';
    if (riskScore >= 0.4) return 'High';
    if (riskScore >= 0.2) return 'Medium';
    return 'Low';
  };

  const getDeviceIcon = (deviceType) => {
    const type = deviceType?.toLowerCase() || '';
    if (type.includes('camera')) return '📹';
    if (type.includes('thermostat')) return '🌡️';
    if (type.includes('speaker')) return '🔊';
    if (type.includes('light')) return '💡';
    if (type.includes('lock')) return '🔒';
    if (type.includes('router')) return '📡';
    if (type.includes('printer')) return '🖨️';
    return '📱';
  };

  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };

  const handleDeviceClick = (device) => {
    setSelectedDevice(selectedDevice?.id === device.id ? null : device);
  };

  return (
    <div className={`App ${darkMode ? 'dark' : 'light'}`}>
      <header className="App-header">
        <div className="header-content">
          <div className="header-left">
            <h1>🔒 IoT Security Dashboard</h1>
            <p>Research-Grade Agentless IoT/IIoT Security Monitoring Platform</p>
          </div>
          <div className="header-controls">
            <button className="theme-toggle" onClick={toggleTheme}>
              {darkMode ? '☀️' : '🌙'}
            </button>
            <button onClick={fetchDevices} className="refresh-btn">
              🔄 Refresh
            </button>
          </div>
        </div>
      </header>

      <main className="App-main">
        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <h3>Total Devices</h3>
              <div className="stat-number">{devices.length}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <h3>Active Devices</h3>
              <div className="stat-number">{devices.filter(d => d.status === 'active').length}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⚠️</div>
            <div className="stat-content">
              <h3>High Risk</h3>
              <div className="stat-number">{devices.filter(d => d.risk_score >= 0.4).length}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🎯</div>
            <div className="stat-content">
              <h3>Avg Confidence</h3>
              <div className="stat-number">
                {devices.length > 0
                  ? Math.round(devices.reduce((sum, d) => sum + d.confidence_score, 0) / devices.length * 100) + '%'
                  : '0%'
                }
              </div>
            </div>
          </div>
        </div>

        <div className="devices-section">
          <div className="section-header">
            <h2>🔍 Discovered Devices</h2>
            <div className="section-controls">
              <span className="device-count">{devices.length} devices found</span>
            </div>
          </div>

          {loading && (
            <div className="loading">
              <div className="loading-spinner"></div>
              <p>Scanning network for IoT devices...</p>
            </div>
          )}

          {error && (
            <div className="error">
              <div className="error-icon">❌</div>
              <div className="error-content">
                <h3>Connection Error</h3>
                <p>{error}</p>
                <button onClick={fetchDevices} className="retry-btn">🔄 Retry</button>
              </div>
            </div>
          )}

          {!loading && !error && devices.length === 0 && (
            <div className="no-devices">
              <div className="no-devices-icon">🔍</div>
              <h3>No Devices Found</h3>
              <p>The system is actively monitoring your network for IoT devices.</p>
              <button onClick={fetchDevices} className="scan-btn">🔄 Scan Again</button>
            </div>
          )}

          {!loading && !error && devices.length > 0 && (
            <div className="devices-grid">
              {devices.map((device) => (
                <div
                  key={device.id}
                  className={`device-card ${selectedDevice?.id === device.id ? 'selected' : ''}`}
                  onClick={() => handleDeviceClick(device)}
                >
                  <div className="device-header">
                    <div className="device-title">
                      <span className="device-icon">{getDeviceIcon(device.device_type)}</span>
                      <div>
                        <h3>{device.device_type || 'Unknown Device'}</h3>
                        <span className="device-vendor">{device.vendor || 'Unknown Vendor'}</span>
                      </div>
                    </div>
                    <div className="device-badges">
                      <div
                        className="risk-badge"
                        style={{ backgroundColor: getRiskColor(device.risk_score) }}
                      >
                        {getRiskLevel(device.risk_score)}
                      </div>
                      <div className={`status-badge ${device.status}`}>
                        {device.status}
                      </div>
                    </div>
                  </div>

                  <div className="device-details">
                    <div className="detail-row">
                      <span className="label">🌐 IP Address</span>
                      <span className="value">{device.ip_address}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">🔗 MAC Address</span>
                      <span className="value">{device.mac_address || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">🎯 Confidence</span>
                      <span className="value">
                        <div className="confidence-bar">
                          <div
                            className="confidence-fill"
                            style={{ width: `${device.confidence_score * 100}%` }}
                          ></div>
                          <span className="confidence-text">{Math.round(device.confidence_score * 100)}%</span>
                        </div>
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="label">⏰ Last Seen</span>
                      <span className="value">{formatDate(device.last_seen)}</span>
                    </div>
                  </div>

                  {selectedDevice?.id === device.id && (
                    <div className="device-expanded">
                      <div className="expanded-section">
                        <h4>📋 Device Information</h4>
                        <div className="info-grid">
                          <div className="info-item">
                            <span className="info-label">Model</span>
                            <span className="info-value">{device.model || 'Unknown'}</span>
                          </div>
                          <div className="info-item">
                            <span className="info-label">Firmware</span>
                            <span className="info-value">{device.firmware_version || 'Unknown'}</span>
                          </div>
                          <div className="info-item">
                            <span className="info-label">First Seen</span>
                            <span className="info-value">{formatDate(device.first_seen)}</span>
                          </div>
                          <div className="info-item">
                            <span className="info-label">Risk Score</span>
                            <span className="info-value">{Math.round(device.risk_score * 100)}%</span>
                          </div>
                        </div>
                      </div>
                      <div className="device-actions">
                        <button className="action-btn primary">🔍 Scan Device</button>
                        <button className="action-btn secondary">📊 View Traffic</button>
                        <button className="action-btn secondary">🚨 View Alerts</button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      <footer className="App-footer">
        <div className="footer-content">
          <p>IoT Security Dashboard v2.0.0 - Research Platform</p>
          <div className="footer-links">
            <a href="http://localhost:5000/docs" target="_blank" rel="noopener noreferrer">📚 API Docs</a>
            <a href="http://localhost:5000/health" target="_blank" rel="noopener noreferrer">💚 Health Check</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;