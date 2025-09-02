import { useState, useRef, useCallback } from 'react';
import type { Message, MessageType, ConnectionStatus, ConnectionInfo } from '../types';
import { api } from '../services/api';

const generateUniqueId = () => Date.now().toString() + Math.random().toString(36).substring(7);

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('DISCONNECTED');
  const [connectionInfo, setConnectionInfo] = useState<ConnectionInfo | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const addMessage = useCallback((type: MessageType, content: string | React.ReactNode) => {
    setMessages(prev => [
      ...prev,
      { id: generateUniqueId(), type, content, timestamp: new Date() },
    ]);
  }, []);

  const handleSendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;
    
    addMessage('user', content);
    setInput('');
    setIsLoading(true);

    const agentMessageId = generateUniqueId();
    let fullResponse = '';
    
    setMessages(prev => [
      ...prev,
      { id: agentMessageId, type: 'agent', content: '', timestamp: new Date() }
    ]);

    api.sendMessage(
      content,
      (data) => {
        if (data.content) {
          fullResponse += data.content;
          setMessages(prev =>
            prev.map(msg =>
              msg.id === agentMessageId ? { ...msg, content: fullResponse } : msg
            )
          );
        }
        if (data.error) {
          addMessage('error', `Agent Error: ${data.error}`);
          setIsLoading(false);
        }
        if (data.status === 'complete') {
          setIsLoading(false);
        }
      },
      (error) => {
        addMessage('error', error.message);
        setIsLoading(false);
      }
    );
  }, [addMessage, isLoading]);

  return {
    messages,
    setMessages,
    input,
    setInput,
    isLoading,
    setIsLoading,
    connectionStatus,
    setConnectionStatus,
    connectionInfo,
    setConnectionInfo,
    messagesEndRef,
    addMessage,
    handleSendMessage,
  };
};
