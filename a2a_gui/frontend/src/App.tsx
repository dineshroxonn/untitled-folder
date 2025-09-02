import React, { useEffect } from 'react';
import { useChat } from './hooks/useChat';
import { useStatus } from './hooks/useStatus';
import { Header } from './components/Header';
import { DiagnosticPanel } from './components/DiagnosticPanel';
import { ChatInterface } from './components/ChatInterface';
import { StatusBar } from './components/StatusBar';
import './App.css';

function App() {
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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8 h-[calc(100vh-200px)]">
          <DiagnosticPanel
            status={connectionStatus}
            info={connectionInfo}
            onConnect={handleConnect}
            onDisconnect={handleDisconnect}
            onScan={handleScan}
            isLoading={isLoading}
          />
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
      </main>
    </div>
  );
}

export default App;