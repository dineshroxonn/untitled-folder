import { Power, AlertCircle, Zap, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';
import type { ConnectionStatus, ConnectionInfo } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface ControlPanelProps {
  status: ConnectionStatus;
  info: ConnectionInfo | null;
  onConnect: () => void;
  onDisconnect: () => void;
  onScan: () => void;
  isLoading: boolean;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({ status, info, onConnect, onDisconnect, onScan, isLoading }) => (
  <div className="lg:col-span-1 space-y-8">
    <Card className="bg-secondary border-primary/20">
      <CardHeader>
        <CardTitle className="flex items-center text-primary">
          <Power className="w-6 h-6 mr-3" />
          Vehicle Connection
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {status === 'DISCONNECTED' && (
            <Button onClick={onConnect} className="w-full">Connect to Vehicle</Button>
          )}
          {status === 'CONNECTING' && (
            <Button className="w-full" disabled>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" /> Connecting...
            </Button>
          )}
          {status === 'CONNECTED' && (
            <Button onClick={onDisconnect} variant="destructive" className="w-full">Disconnect</Button>
          )}
          {status === 'ERROR' && (
             <Button onClick={onConnect} className="w-full">Retry Connection</Button>
          )}
        </div>
        <div className="mt-6 text-base text-muted-foreground">
          <p><strong>Status:</strong> <span className={clsx('font-semibold', {
            'text-green-400': status === 'CONNECTED',
            'text-red-400': status === 'ERROR' || status === 'DISCONNECTED',
            'text-yellow-400': status === 'CONNECTING',
          })}>{status}</span></p>
          {info?.connected && (
            <div className="mt-2 space-y-1">
              <p><strong>Port:</strong> {info.port || 'N/A'}</p>
              <p><strong>Protocol:</strong> {info.protocol || 'N/A'}</p>
            </div>
          )}
        </div>
        <div className="mt-6 border-t border-primary/20 pt-6">
          <Button
            onClick={onScan}
            disabled={status !== 'CONNECTED' || isLoading}
            className="w-full text-lg"
          >
            <Zap className="w-5 h-5 mr-2" /> Scan Vehicle
          </Button>
        </div>
      </CardContent>
    </Card>
    <Card className="bg-secondary border-primary/20">
      <CardHeader>
        <CardTitle className="flex items-center text-primary">
          <AlertCircle className="w-6 h-6 mr-3" />
          Instructions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 text-base text-muted-foreground">
          <p>1. Click <strong>Connect to Vehicle</strong> to link with your OBD-II adapter.</p>
          <p>2. Once connected, click <strong>Scan Vehicle</strong> for a full diagnostic report.</p>
          <p>3. You can also type manual queries or DTCs in the chat.</p>
        </div>
      </CardContent>
    </Card>
  </div>
);