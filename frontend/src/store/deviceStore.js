import { create } from 'zustand';

const useDeviceStore = create((set, get) => ({
  devices: [],
  selectedDevice: null,
  loading: false,
  error: null,

  setDevices: (devices) => set({ devices }),
  setSelectedDevice: (device) => set({ selectedDevice: device }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  addDevice: (device) => set((state) => ({
    devices: [...state.devices, device]
  })),

  updateDevice: (deviceId, updates) => set((state) => ({
    devices: state.devices.map(device =>
      device.id === deviceId ? { ...device, ...updates } : device
    )
  })),

  removeDevice: (deviceId) => set((state) => ({
    devices: state.devices.filter(device => device.id !== deviceId)
  })),

  getDeviceById: (deviceId) => {
    const { devices } = get();
    return devices.find(device => device.id === deviceId);
  },

  getDevicesByType: (deviceType) => {
    const { devices } = get();
    return devices.filter(device => device.device_type === deviceType);
  },

  getOnlineDevices: () => {
    const { devices } = get();
    return devices.filter(device => device.status === 'online');
  },

  getHighRiskDevices: () => {
    const { devices } = get();
    return devices.filter(device => device.risk_score > 0.7);
  }
}));

export { useDeviceStore };