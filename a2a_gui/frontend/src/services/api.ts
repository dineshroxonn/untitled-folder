import type { StreamChunk } from '../types';

export const api = {
  checkAgentStatus: () => fetch('/agent-status').then(res => res.json()),
  getConnectionInfo: () => fetch('/connection-info').then(res => res.json()),
  connectObd: () => fetch('/connect-obd', { method: 'POST' }),
  disconnectObd: () => fetch('/disconnect-obd', { method: 'POST' }),
  sendMessage: (message: string, onChunk: (chunk: StreamChunk) => void, onError: (err: Error) => void) => {
    const eventSource = new EventSource(`/diagnose?message=${encodeURIComponent(message)}`);
    eventSource.onmessage = event => {
      try {
        const data: StreamChunk = JSON.parse(event.data);
        onChunk(data);
      } catch (error) {
        console.warn('Failed to parse SSE data:', event.data, error);
      }
    };
    eventSource.onerror = () => {
      onError(new Error('Connection to the diagnostic stream failed.'));
      eventSource.close();
    };
    return () => eventSource.close();
  }
};
