export type MessageType = 'user' | 'agent' | 'error' | 'info';
export type ConnectionStatus = 'DISCONNECTED' | 'CONNECTING' | 'CONNECTED' | 'ERROR';

export interface Message {
  id: string;
  type: MessageType;
  content: string | React.ReactNode;
  timestamp: Date;
}

export interface AgentStatus {
  available: boolean;
  agent_url?: string;
}

export interface ConnectionInfo {
  connected: boolean;
  port?: string;
  protocol?: string;
}

export interface StreamChunk {
  content?: string;
  error?: string;
  status?: 'complete';
}