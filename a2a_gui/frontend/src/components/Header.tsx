import React from 'react';
import { Car, Zap, Shield, Activity } from 'lucide-react';
import { clsx } from 'clsx';
import type { AgentStatus } from '../types';

export const Header: React.FC<{ agentStatus: AgentStatus }> = ({ agentStatus }) => (
  <header className="relative bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50 shadow-2xl">
    <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-cyan-600/10" />
    <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between h-24">
        <div className="flex items-center space-x-6">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl blur-lg opacity-30" />
            <div className="relative bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-2xl">
              <Car className="h-8 w-8 text-white" />
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              AI Car Diagnostic
            </h1>
            <p className="text-slate-400 font-medium flex items-center mt-1">
              <Zap className="w-4 h-4 mr-2" />
              Your Intelligent Vehicle Assistant
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-6">
          <div className="hidden md:flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
              <Shield className="w-4 h-4 text-green-400" />
              <span className="text-slate-300">Secure Connection</span>
            </div>
            <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
              <Activity className="w-4 h-4 text-blue-400" />
              <span className="text-slate-300">Real-time Diagnostics</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div
              className={clsx(
                "w-3 h-3 rounded-full transition-all duration-300",
                agentStatus.available 
                  ? "bg-green-500 shadow-lg shadow-green-500/50 animate-pulse" 
                  : "bg-red-500 shadow-lg shadow-red-500/50"
              )}
            />
            <div className="text-right">
              <div className="text-sm font-semibold text-slate-200">
                {agentStatus.available ? "Agent Online" : "Agent Offline"}
              </div>
              <div className="text-xs text-slate-400">
                {agentStatus.available ? "Ready for diagnostics" : "Reconnecting..."}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
);
