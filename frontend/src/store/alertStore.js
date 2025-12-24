import { create } from 'zustand';

const useAlertStore = create((set, get) => ({
  alerts: [],
  selectedAlert: null,
  loading: false,
  error: null,

  setAlerts: (alerts) => set({ alerts }),
  setSelectedAlert: (alert) => set({ selectedAlert: alert }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts]
  })),

  updateAlert: (alertId, updates) => set((state) => ({
    alerts: state.alerts.map(alert =>
      alert.id === alertId ? { ...alert, ...updates } : alert
    )
  })),

  removeAlert: (alertId) => set((state) => ({
    alerts: state.alerts.filter(alert => alert.id !== alertId)
  })),

  getAlertById: (alertId) => {
    const { alerts } = get();
    return alerts.find(alert => alert.id === alertId);
  },

  getAlertsBySeverity: (severity) => {
    const { alerts } = get();
    return alerts.filter(alert => alert.severity === severity);
  },

  getActiveAlerts: () => {
    const { alerts } = get();
    return alerts.filter(alert => alert.status === 'open');
  },

  getCriticalAlerts: () => {
    const { alerts } = get();
    return alerts.filter(alert => alert.severity === 'CRITICAL');
  }
}));

export { useAlertStore };