import React, { useState, useEffect } from 'react';
import Dashboard from '../components/Dashboard';
import { getDashboardMetrics } from '../services/api';

const Home = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const data = await getDashboardMetrics();
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="home-page">
      <Dashboard metrics={metrics} />
    </div>
  );
};

export default Home;