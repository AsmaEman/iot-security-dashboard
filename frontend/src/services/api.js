import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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
    return Promise.reject(error);
  }
);

// Dashboard APIs
export const getDashboardMetrics = () => api.get('/dashboard/metrics');

// Device APIs
export const getDevices = (params = {}) => api.get('/devices', { params });
export const getDevice = (deviceId) => api.get(`/devices/${deviceId}`);
export const scanDevice = (deviceId) => api.post(`/devices/${deviceId}/scan`);

// Alert APIs
export const getAlerts = (params = {}) => api.get('/alerts', { params });
export const updateAlert = (alertId, data) => api.patch(`/alerts/${alertId}`, data);

// Vulnerability APIs
export const getVulnerabilities = (params = {}) => api.get('/vulnerabilities', { params });

// Network Traffic APIs
export const getNetworkTraffic = (params = {}) => api.get('/network-traffic', { params });

export default api;