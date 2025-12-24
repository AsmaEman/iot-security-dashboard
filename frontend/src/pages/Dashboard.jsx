import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  DevicesOther as DevicesIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  BugReport as VulnIcon,
  NetworkCheck as NetworkIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';

// Import components
import KPICard from '../components/common/KPICard';
import LineChart from '../components/common/LineChart';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

// Import services
import { getDashboardMetrics } from '../services/api';
import { useDeviceStore } from '../store/deviceStore';
import { useAlertStore } from '../store/alertStore';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { devices } = useDeviceStore();
  const { alerts } = useAlertStore();

  useEffect(() => {
    fetchDashboardData();

    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const data = await getDashboardMetrics();
      setMetrics(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard metrics:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  // Mock data for charts (in real implementation, this would come from the API)
  const deviceStatusData = [
    { name: 'Online', value: metrics?.online_devices || 4, color: '#4CAF50' },
    { name: 'Offline', value: metrics?.offline_devices || 1, color: '#F44336' },
    { name: 'Warning', value: 1, color: '#FF9800' },
  ];

  const riskDistributionData = [
    { name: 'Low Risk', value: 60, color: '#4CAF50' },
    { name: 'Medium Risk', value: 25, color: '#FF9800' },
    { name: 'High Risk', value: 15, color: '#F44336' },
  ];

  const alertTrendData = [
    { time: '00:00', alerts: 2 },
    { time: '04:00', alerts: 1 },
    { time: '08:00', alerts: 4 },
    { time: '12:00', alerts: 3 },
    { time: '16:00', alerts: 6 },
    { time: '20:00', alerts: 2 },
  ];

  const protocolData = [
    { protocol: 'HTTPS', count: 450 },
    { protocol: 'MQTT', count: 320 },
    { protocol: 'HTTP', count: 180 },
    { protocol: 'Modbus', count: 95 },
    { protocol: 'OPC-UA', count: 60 },
  ];

  return (
    <Box>
      {/* Page Header */}
      <Box mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          IoT Security Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time monitoring and threat detection for IoT/IIoT devices
        </Typography>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={2}>
          <KPICard
            title="Total Devices"
            value={metrics?.total_devices || 5}
            icon={<DevicesIcon />}
            color="primary"
            trend="+2 this week"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <KPICard
            title="Online Devices"
            value={metrics?.online_devices || 4}
            icon={<NetworkIcon />}
            color="success"
            trend="80% uptime"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <KPICard
            title="Active Alerts"
            value={metrics?.active_alerts || 3}
            icon={<WarningIcon />}
            color="warning"
            trend="-1 from yesterday"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <KPICard
            title="Vulnerabilities"
            value={metrics?.critical_vulnerabilities || 1}
            icon={<VulnIcon />}
            color="error"
            trend="2 patched"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <KPICard
            title="Avg Risk Score"
            value={`${metrics?.average_risk_score || 87.6}%`}
            icon={<SecurityIcon />}
            color="info"
            trend="+2.1% improvement"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <KPICard
            title="Anomalies (24h)"
            value={metrics?.network_anomalies_24h || 23}
            icon={<TrendingIcon />}
            color="secondary"
            trend="Normal range"
          />
        </Grid>
      </Grid>

      {/* Charts Row 1 */}
      <Grid container spacing={3} mb={3}>
        {/* Device Status Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Device Status Distribution
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={deviceStatusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {deviceStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Score Distribution
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskDistributionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {riskDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row 2 */}
      <Grid container spacing={3} mb={3}>
        {/* Alert Trends */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alert Trends (Last 24 Hours)
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={alertTrendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="alerts" fill="#FF6384" name="Security Alerts" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Protocol Usage */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Protocol Usage
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={protocolData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="protocol" type="category" width={60} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#36A2EB" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Status */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="success.main">
                      99.2%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Device ID Accuracy
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="success.main">
                      96.7%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Anomaly Detection Rate
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="warning.main">
                      2.3%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      False Positive Rate
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="info.main">
                      &lt;5s
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Detection Latency
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Last Updated */}
      <Box mt={2} textAlign="center">
        <Typography variant="caption" color="text.secondary">
          Last updated: {metrics?.last_updated ? new Date(metrics.last_updated).toLocaleString() : 'Never'}
        </Typography>
      </Box>
    </Box>
  );
};

export default Dashboard;