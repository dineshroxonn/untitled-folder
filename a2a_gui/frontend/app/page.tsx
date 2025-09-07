"use client"
import React, { useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import { useStatus } from '../hooks/useStatus';
import { Header } from '../components/Header';
import { DiagnosticPanel } from '../components/DiagnosticPanel';
import { ChatInterface } from '../components/ChatInterface';
import { StatusBar } from '../components/StatusBar';

export default function Page() {
  const {
    messages,
    input,
    setInput,
    isLoading,
    messagesEndRef,
    addMessage,
    handleSendMessage,
  } = useChat();

  const {
    agentStatus,
    connectionStatus,
    connectionInfo,
    handleConnect,
    handleDisconnect,
  } = useStatus(addMessage);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, messagesEndRef]);

  const handleScan = () => {
    handleSendMessage("Scan my vehicle for trouble codes and live data.");
  };

  return (
    <div className="dark min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 font-sans text-foreground">
      <Header agentStatus={agentStatus} />
      <StatusBar 
        agentStatus={agentStatus}
        connectionStatus={connectionStatus}
        connectionInfo={connectionInfo}
      />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 sm:gap-6 md:gap-8 h-[calc(100vh-160px)] sm:h-[calc(100vh-180px)]">
          <div className="lg:col-span-1">
            <DiagnosticPanel
              status={connectionStatus}
              info={connectionInfo}
              onConnect={handleConnect}
              onDisconnect={handleDisconnect}
              onScan={handleScan}
              isLoading={isLoading}
            />
          </div>
          <div className="lg:col-span-3">
            <ChatInterface
              messages={messages}
              input={input}
              setInput={setInput}
              isLoading={isLoading}
              agentAvailable={agentStatus.available}
              onSendMessage={() => handleSendMessage(input)}
              messagesEndRef={messagesEndRef}
            />
          </div>
        </div>
      </main>
    </div>
  );
}