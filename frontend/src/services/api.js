import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);

    // Handle specific error cases
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

// Dashboard APIs
export const getDashboardMetrics = () => {
  // Mock data for development
  return Promise.resolve({
    total_devices: 5,
    online_devices: 4,
    offline_devices: 1,
    high_risk_devices: 1,
    active_alerts: 3,
    critical_vulnerabilities: 1,
    network_anomalies_24h: 23,
    average_risk_score: 87.6,
    last_updated: new Date().toISOString()
  });
};

// Device APIs
export const getDevices = (params = {}) => api.get('/api/devices', { params });
export const getDevice = (deviceId) => api.get(`/api/devices/${deviceId}`);
export const updateDevice = (deviceId, data) => api.put(`/api/devices/${deviceId}`, data);
export const deleteDevice = (deviceId) => api.delete(`/api/devices/${deviceId}`);
export const fingerprintDevice = (deviceId) => api.post(`/api/devices/${deviceId}/fingerprint`);
export const scanDevice = (deviceId) => api.post(`/api/devices/${deviceId}/scan`);
export const getDeviceAlerts = (deviceId, params = {}) => api.get(`/api/devices/${deviceId}/alerts`, { params });
export const getDeviceVulnerabilities = (deviceId, params = {}) => api.get(`/api/devices/${deviceId}/vulnerabilities`, { params });
export const getDeviceTraffic = (deviceId, params = {}) => api.get(`/api/devices/${deviceId}/traffic`, { params });

// Alert APIs
export const getAlerts = (params = {}) => api.get('/api/alerts', { params });
export const getAlert = (alertId) => api.get(`/api/alerts/${alertId}`);
export const updateAlert = (alertId, data) => api.put(`/api/alerts/${alertId}`, data);
export const deleteAlert = (alertId) => api.delete(`/api/alerts/${alertId}`);
export const getAlertStats = () => api.get('/api/alerts/stats');
export const bulkResolveAlerts = (alertIds) => api.post('/api/alerts/bulk-resolve', { alert_ids: alertIds });

// Vulnerability APIs
export const getVulnerabilities = (params = {}) => api.get('/api/vulnerabilities', { params });
export const getVulnerability = (vulnId) => api.get(`/api/vulnerabilities/${vulnId}`);
export const updateVulnerability = (vulnId, data) => api.put(`/api/vulnerabilities/${vulnId}`, data);

// Dataset APIs
export const processDataset = (data) => api.post('/api/datasets/process', data);
export const getDatasetStatus = (datasetName) => api.get(`/api/datasets/${datasetName}/status`);
export const getDatasetMetrics = (datasetName) => api.get(`/api/datasets/${datasetName}/metrics`);
export const analyzeDataset = (datasetName) => api.post(`/api/datasets/${datasetName}/analyze`);

// ML Model APIs
export const getMLModels = () => api.get('/api/ml/models');
export const trainModel = (data) => api.post('/api/ml/models/train', data);
export const getModelDetails = (modelName) => api.get(`/api/ml/models/${modelName}`);
export const getModelMetrics = (modelName) => api.get(`/api/ml/models/${modelName}/metrics`);
export const makePrediction = (modelName, data) => api.post(`/api/ml/models/${modelName}/predict`, data);

// Research APIs
export const getResearchDatasets = () => api.get('/api/research/datasets');
export const getResearchMetrics = () => api.get('/api/research/metrics');
export const getModelComparison = () => api.get('/api/research/comparison');
export const runExperiment = (data) => api.post('/api/research/experiment', data);

// Authentication APIs
export const login = (credentials) => api.post('/api/auth/login', credentials);
export const refreshToken = () => api.post('/api/auth/refresh');
export const logout = () => api.post('/api/auth/logout');
export const getProfile = () => api.get('/api/auth/profile');

// System APIs
export const getHealth = () => api.get('/health');
export const getMetrics = () => api.get('/metrics');

export default api;