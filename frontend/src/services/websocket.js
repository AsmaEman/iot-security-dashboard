import { useEffect, useRef } from 'react';
import { toast } from 'react-toastify';
import { useDeviceStore } from '../store/deviceStore';
import { useAlertStore } from '../store/alertStore';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:5000/ws';

export const useWebSocket = () => {
  const ws = useRef(null);
  const { updateDevice, addDevice } = useDeviceStore();
  const { addAlert, updateAlert } = useAlertStore();

  useEffect(() => {
    const connect = () => {
      ws.current = new WebSocket(WS_URL);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        toast.success('Real-time connection established');
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        toast.warning('Real-time connection lost. Reconnecting...');

        // Reconnect after 3 seconds
        setTimeout(connect, 3000);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('Connection error occurred');
      };
    };

    const handleWebSocketMessage = (message) => {
      switch (message.type) {
        case 'device_update':
          updateDevice(message.data.id, message.data);
          toast.info(`Device ${message.data.ip_address} updated`);
          break;

        case 'new_device':
          addDevice(message.data);
          toast.success(`New device discovered: ${message.data.ip_address}`);
          break;

        case 'new_alert':
          addAlert(message.data);
          const severity = message.data.severity.toLowerCase();
          const toastMethod = severity === 'critical' ? toast.error :
            severity === 'high' ? toast.warning : toast.info;
          toastMethod(`New ${severity} alert: ${message.data.title}`);
          break;

        case 'alert_update':
          updateAlert(message.data.id, message.data);
          if (message.data.status === 'resolved') {
            toast.success(`Alert resolved: ${message.data.title}`);
          }
          break;

        case 'metrics_update':
          // Handle metrics updates
          console.log('Metrics updated:', message.data);
          break;

        case 'heartbeat':
          // Handle heartbeat response
          console.log('Heartbeat received');
          break;

        default:
          console.log('Unknown message type:', message.type);
      }
    };

    connect();

    // Cleanup on unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [updateDevice, addDevice, addAlert, updateAlert]);

  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return { sendMessage };
};