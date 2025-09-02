import { Car } from 'lucide-react';
import { clsx } from 'clsx';
import type { AgentStatus } from '../types';

export const Header: React.FC<{ agentStatus: AgentStatus }> = ({ agentStatus }) => (
  <header className="bg-secondary shadow-md">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between h-20">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Car className="h-10 w-10 text-primary" />
          </div>
          <div className="ml-4">
            <h1 className="text-3xl font-bold text-primary">AI Car Diagnostic</h1>
            <p className="text-sm font-medium text-muted-foreground">
              Your Virtual Mechanic Assistant
            </p>
          </div>
        </div>
        <div className="flex items-center">
          <div
            className={clsx("w-3 h-3 rounded-full mr-2 animate-pulse", {
              "bg-green-500": agentStatus.available,
              "bg-red-500": !agentStatus.available,
            })}
          />
          <span className="text-sm font-medium text-muted-foreground">
            {agentStatus.available ? "Agent Online" : "Agent Offline"}
          </span>
        </div>
      </div>
    </div>
  </header>
);