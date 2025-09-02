import React, { useState } from 'react';
import { 
  Power, 
  Zap, 
  Loader2, 
  Car, 
  Settings, 
  Info,
  ChevronDown,
  ChevronUp,
  Gauge,
  AlertCircle,
  CheckCircle2,
  Wrench
} from 'lucide-react';
import { clsx } from 'clsx';
import type { ConnectionStatus, ConnectionInfo } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface DiagnosticPanelProps {
  status: ConnectionStatus;
  info: ConnectionInfo | null;
  onConnect: () => void;
  onDisconnect: () => void;
  onScan: () => void;
  isLoading: boolean;
}

export const DiagnosticPanel: React.FC<DiagnosticPanelProps> = ({ 
  status, 
  info, 
  onConnect, 
  onDisconnect, 
  onScan, 
  isLoading 
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const getStatusIcon = () => {
    switch (status) {
      case 'CONNECTED': return <CheckCircle2 className="w-5 h-5 text-green-400" />;
      case 'CONNECTING': return <Loader2 className="w-5 h-5 text-yellow-400 animate-spin" />;
      case 'ERROR': return <AlertCircle className="w-5 h-5 text-red-400" />;
      default: return <Power className="w-5 h-5 text-slate-400" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'CONNECTED': return 'Vehicle Connected';
      case 'CONNECTING': return 'Establishing Connection';
      case 'ERROR': return 'Connection Failed';
      default: return 'Ready to Connect';
    }
  };

  const getStatusDescription = () => {
    switch (status) {
      case 'CONNECTED': return 'OBD-II adapter is connected and ready for diagnostics';
      case 'CONNECTING': return 'Attempting to establish connection with your vehicle';
      case 'ERROR': return 'Unable to connect to OBD-II adapter. Check connections.';
      default: return 'Connect your OBD-II adapter to begin vehicle diagnostics';
    }
  };

  return (
    <div className="xl:col-span-1 space-y-6">
      {/* Main Connection Card */}
      <Card className={clsx(
        "glass-effect hover-lift transition-all duration-500 border-slate-700/50",
        status === 'CONNECTED' && "connection-glow"
      )}>
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {getStatusIcon()}
              <span className="text-lg font-semibold text-slate-100">
                Vehicle Connection
              </span>
            </div>
            <div className={clsx(
              "px-2 py-1 rounded-full text-xs font-medium border",
              status === 'CONNECTED' ? "bg-green-500/10 text-green-400 border-green-500/20" :
              status === 'CONNECTING' ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/20" :
              status === 'ERROR' ? "bg-red-500/10 text-red-400 border-red-500/20" :
              "bg-slate-500/10 text-slate-400 border-slate-500/20"
            )}>
              {status}
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-slate-300">{getStatusText()}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              {getStatusDescription()}
            </p>
          </div>

          {/* Connection Actions */}
          <div className="space-y-3">
            {status === 'DISCONNECTED' && (
              <Button 
                onClick={onConnect} 
                className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                <Power className="w-5 h-5 mr-2" />
                Connect to Vehicle
              </Button>
            )}
            
            {status === 'CONNECTING' && (
              <Button className="w-full h-12" disabled>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Establishing Connection...
              </Button>
            )}
            
            {status === 'CONNECTED' && (
              <div className="space-y-3">
                <Button 
                  onClick={onScan}
                  disabled={isLoading}
                  className={clsx(
                    "w-full h-12 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium transition-all duration-300 shadow-lg hover:shadow-xl",
                    isLoading && "scan-animation"
                  )}
                >
                  <Zap className="w-5 h-5 mr-2" />
                  {isLoading ? 'Scanning Vehicle...' : 'Run Full Diagnostic'}
                </Button>
                
                <Button 
                  onClick={onDisconnect} 
                  variant="outline"
                  className="w-full h-10 border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white transition-all duration-300"
                >
                  Disconnect
                </Button>
              </div>
            )}
            
            {status === 'ERROR' && (
              <Button 
                onClick={onConnect} 
                className="w-full h-12 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white font-medium transition-all duration-300"
              >
                <Power className="w-5 h-5 mr-2" />
                Retry Connection
              </Button>
            )}
          </div>

          {/* Connection Details */}
          {info?.connected && (
            <div className="space-y-4 pt-4 border-t border-slate-700/50">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <div className="text-xs font-medium text-slate-400 uppercase tracking-wide">Port</div>
                  <div className="text-sm text-slate-200 font-mono bg-slate-800/50 px-2 py-1 rounded">
                    {info.port || 'N/A'}
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="text-xs font-medium text-slate-400 uppercase tracking-wide">Protocol</div>
                  <div className="text-sm text-slate-200 font-mono bg-slate-800/50 px-2 py-1 rounded">
                    {info.protocol || 'N/A'}
                  </div>
                </div>
              </div>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="w-full text-slate-400 hover:text-slate-200 transition-colors duration-200"
              >
                <Settings className="w-4 h-4 mr-2" />
                Advanced Settings
                {showAdvanced ? <ChevronUp className="w-4 h-4 ml-2" /> : <ChevronDown className="w-4 h-4 ml-2" />}
              </Button>
              
              {showAdvanced && (
                <div className="space-y-3 pt-3 border-t border-slate-700/30">
                  <div className="grid grid-cols-1 gap-3 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Baudrate:</span>
                      <span className="text-slate-200 font-mono">38400</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Timeout:</span>
                      <span className="text-slate-200 font-mono">30s</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Auto-detect:</span>
                      <span className="text-green-400 font-mono">Enabled</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions Card */}
      <Card className="glass-effect hover-lift border-slate-700/50">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center text-slate-100">
            <Gauge className="w-5 h-5 mr-3 text-blue-400" />
            Quick Actions
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 gap-3">
            <Button
              variant="outline"
              size="sm"
              disabled={status !== 'CONNECTED' || isLoading}
              className="justify-start border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white transition-all duration-300"
            >
              <Car className="w-4 h-4 mr-2" />
              Read Vehicle Info
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              disabled={status !== 'CONNECTED' || isLoading}
              className="justify-start border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white transition-all duration-300"
            >
              <AlertCircle className="w-4 h-4 mr-2" />
              Check Engine Codes
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              disabled={status !== 'CONNECTED' || isLoading}
              className="justify-start border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white transition-all duration-300"
            >
              <Gauge className="w-4 h-4 mr-2" />
              Live Engine Data
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Instructions Card */}
      <Card className="glass-effect border-slate-700/50">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center text-slate-100">
            <Info className="w-5 h-5 mr-3 text-cyan-400" />
            Getting Started
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm text-slate-300">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold text-blue-400">1</span>
              </div>
              <div>
                <p className="font-medium text-slate-200">Connect OBD-II Adapter</p>
                <p className="text-slate-400 text-xs mt-1">Plug adapter into your vehicle's diagnostic port</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold text-purple-400">2</span>
              </div>
              <div>
                <p className="font-medium text-slate-200">Turn On Ignition</p>
                <p className="text-slate-400 text-xs mt-1">Engine doesn't need to be running</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-bold text-green-400">3</span>
              </div>
              <div>
                <p className="font-medium text-slate-200">Start Diagnostics</p>
                <p className="text-slate-400 text-xs mt-1">Click connect and run full diagnostic scan</p>
              </div>
            </div>
          </div>
          
          <div className="mt-6 pt-4 border-t border-slate-700/30">
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <Wrench className="w-4 h-4" />
              <span>Professional-grade OBD-II diagnostics</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
