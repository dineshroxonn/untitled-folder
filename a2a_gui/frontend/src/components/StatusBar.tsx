import React from 'react';
import { Wifi, WifiOff, Bluetooth, Usb, AlertTriangle, CheckCircle } from 'lucide-react';
import { clsx } from 'clsx';
import type { AgentStatus, ConnectionStatus, ConnectionInfo } from '../types';

interface StatusBarProps {
  agentStatus: AgentStatus;
  connectionStatus: ConnectionStatus;
  connectionInfo: ConnectionInfo | null;
}

export const StatusBar: React.FC<StatusBarProps> = ({ 
  agentStatus, 
  connectionStatus, 
  connectionInfo 
}) => {
  const getConnectionIcon = () => {
    if (!connectionInfo?.port) return <WifiOff className="w-4 h-4" />;
    
    if (connectionInfo.port.includes('bluetooth') || connectionInfo.port.includes('rfcomm')) {
      return <Bluetooth className="w-4 h-4" />;
    }
    if (connectionInfo.port.includes('USB') || connectionInfo.port.includes('tty')) {
      return <Usb className="w-4 h-4" />;
    }
    return <Wifi className="w-4 h-4" />;
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'CONNECTED': return 'text-green-400 bg-green-500/10 border-green-500/20';
      case 'CONNECTING': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      case 'ERROR': return 'text-red-400 bg-red-500/10 border-red-500/20';
      default: return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
    }
  };

  return (
    <div className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-700/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-12">
          <div className="flex items-center space-x-6">
            <div className={clsx(
              "flex items-center space-x-2 px-3 py-1.5 rounded-lg border transition-all duration-300",
              getStatusColor()
            )}>
              {getConnectionIcon()}
              <span className="text-sm font-medium">
                {connectionStatus === 'CONNECTED' ? 'Vehicle Connected' : 
                 connectionStatus === 'CONNECTING' ? 'Connecting...' :
                 connectionStatus === 'ERROR' ? 'Connection Error' : 'Disconnected'}
              </span>
            </div>
            
            {connectionInfo?.connected && (
              <div className="hidden sm:flex items-center space-x-4 text-xs text-slate-400">
                <span>Port: {connectionInfo.port}</span>
                <span>•</span>
                <span>Protocol: {connectionInfo.protocol}</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            <div className={clsx(
              "flex items-center space-x-2 px-3 py-1.5 rounded-lg border transition-all duration-300",
              agentStatus.available 
                ? "text-green-400 bg-green-500/10 border-green-500/20"
                : "text-red-400 bg-red-500/10 border-red-500/20"
            )}>
              {agentStatus.available ? (
                <CheckCircle className="w-4 h-4" />
              ) : (
                <AlertTriangle className="w-4 h-4" />
              )}
              <span className="text-sm font-medium">
                AI {agentStatus.available ? 'Ready' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
