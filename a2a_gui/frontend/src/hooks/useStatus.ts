import { useState, useEffect, useCallback } from 'react';
import type { AgentStatus, ConnectionInfo, ConnectionStatus } from '../types';
import { api } from '../services/api';

export const useStatus = (addMessage: (type: 'info' | 'error', content: string) => void) => {
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({ available: false });
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('DISCONNECTED');
  const [connectionInfo, setConnectionInfo] = useState<ConnectionInfo | null>(null);

  const checkStatus = useCallback(async () => {
    try {
      const status = await api.checkAgentStatus();
      setAgentStatus(status);
      if (status.available) {
        const connInfo = await api.getConnectionInfo();
        setConnectionInfo(connInfo);
        setConnectionStatus(connInfo.connected ? 'CONNECTED' : 'DISCONNECTED');
      }
    } catch {
      setAgentStatus({ available: false });
      setConnectionStatus('ERROR');
    }
  }, []);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 10000); // Re-check every 10 seconds
    return () => clearInterval(interval);
  }, [checkStatus]);

  const handleConnect = async () => {
    setConnectionStatus('CONNECTING');
    addMessage('info', 'Attempting to connect to vehicle...');
    try {
      const response = await api.connectObd();
      const data = await response.json();
      if (response.ok && data.success) {
        setConnectionStatus('CONNECTED');
        setConnectionInfo({ connected: true, ...data.data });
        addMessage('info', '✅ Successfully connected to vehicle!');
      } else {
        throw new Error(data.error_message || 'Failed to connect');
      }
    } catch (e: unknown) {
      setConnectionStatus('ERROR');
      const message = e instanceof Error ? e.message : String(e);
      addMessage('error', `Connection Error: ${message}`);
    }
  };

  const handleDisconnect = async () => {
    addMessage('info', 'Disconnecting from vehicle...');
    try {
      await api.disconnectObd();
      setConnectionStatus('DISCONNECTED');
      setConnectionInfo({ connected: false });
      addMessage('info', '🔌 Vehicle disconnected.');
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : String(e);
      addMessage('error', `Failed to disconnect: ${message}`);
    }
  };

  return {
    agentStatus,
    connectionStatus,
    connectionInfo,
    handleConnect,
    handleDisconnect,
  };
};
