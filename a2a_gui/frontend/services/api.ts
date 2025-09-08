import type { StreamChunk } from '../types';

export const api = {
  checkAgentStatus: () => fetch('/api/agent-status').then(res => res.json()),
  getConnectionInfo: () => fetch('/api/connection-info').then(res => res.json()),
  connectObd: (config: any = null) => fetch('/api/connect-obd', { 
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ config })
  }),
  disconnectObd: () => fetch('/api/disconnect-obd', { method: 'POST' }),
  sendMessage: (message: string, onChunk: (chunk: StreamChunk) => void, onError: (err: Error) => void) => {
    const eventSource = new EventSource(`/api/diagnose?message=${encodeURIComponent(message)}`);
    eventSource.onmessage = event => {
      if (event.data.startsWith('{')) {
        try {
          const data: StreamChunk = JSON.parse(event.data);
          onChunk(data);
        } catch (error) {
          console.warn('Failed to parse SSE JSON data:', event.data, error);
        }
      }
    };
    eventSource.onerror = (event) => {
      console.error('EventSource error:', event);
      onError(new Error('Connection to the diagnostic stream failed.'));
      eventSource.close();
    };
    return () => eventSource.close();
  }
};
