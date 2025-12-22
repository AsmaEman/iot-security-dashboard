import React from 'react';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

const Dashboard = ({ metrics }) => {
  if (!metrics) {
    return <div>Loading dashboard metrics...</div>;
  }

  const securityScoreData = {
    labels: ['Excellent', 'Good', 'Fair', 'Poor'],
    datasets: [
      {
        data: [2, 1, 1, 1],
        backgroundColor: ['#4CAF50', '#8BC34A', '#FF9800', '#F44336'],
        borderWidth: 0,
      },
    ],
  };

  const alertTrendData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Security Alerts',
        data: [12, 19, 8, 15, 22, 8, 14],
        borderColor: '#FF6384',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.4,
      },
    ],
  };

  const deviceStatusData = {
    labels: ['Online', 'Offline', 'Warning'],
    datasets: [
      {
        data: [metrics.online_devices, metrics.offline_devices, 1],
        backgroundColor: ['#4CAF50', '#9E9E9E', '#FF9800'],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>IoT Security Dashboard</h2>
        <p>Real-time monitoring and threat detection</p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">🔗</div>
          <div className="metric-content">
            <h3>Total Devices</h3>
            <span className="metric-value">{metrics.total_devices}</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">✅</div>
          <div className="metric-content">
            <h3>Online Devices</h3>
            <span className="metric-value">{metrics.online_devices}</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🛡️</div>
          <div className="metric-content">
            <h3>Avg Security Score</h3>
            <span className="metric-value">{metrics.average_security_score}</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⚠️</div>
          <div className="metric-content">
            <h3>Active Alerts</h3>
            <span className="metric-value">{metrics.active_alerts}</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🚨</div>
          <div className="metric-content">
            <h3>Critical Vulnerabilities</h3>
            <span className="metric-value">{metrics.critical_vulnerabilities}</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <h3>Network Anomalies (24h)</h3>
            <span className="metric-value">{metrics.network_anomalies_24h}</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Device Status Distribution</h3>
          <Doughnut
            data={deviceStatusData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'bottom',
                },
              },
            }}
          />
        </div>

        <div className="chart-container">
          <h3>Security Score Distribution</h3>
          <Doughnut
            data={securityScoreData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'bottom',
                },
              },
            }}
          />
        </div>

        <div className="chart-container wide">
          <h3>Alert Trends (Last 7 Days)</h3>
          <Line
            data={alertTrendData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'top',
                },
                title: {
                  display: false,
                },
              },
              scales: {
                y: {
                  beginAtZero: true,
                },
              },
            }}
          />
        </div>
      </div>

      <div className="dashboard-footer">
        <p>Last updated: {new Date(metrics.last_updated).toLocaleString()}</p>
      </div>
    </div>
  );
};

export default Dashboard;