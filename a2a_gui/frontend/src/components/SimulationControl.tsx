import React, { useState } from 'react';
import { 
  Zap, 
  Loader2,
  Car,
  Wrench
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SimulationControlProps {
  onSimulate: (scenario: string) => void;
  isLoading: boolean;
  addMessage: (type: 'info' | 'error', content: string) => void;
}

const SCENARIOS = [
  { id: "healthy", name: "Healthy Car", description: "No diagnostic trouble codes" },
  { id: "rich_condition", name: "Rich Condition", description: "P0171, P0174 - System too lean" },
  { id: "misfire", name: "Engine Misfire", description: "P0300, P0301 - Random misfire" },
  { id: "catalyst", name: "Catalyst Issue", description: "P0420 - Catalyst efficiency" }
];

export const SimulationControl: React.FC<SimulationControlProps> = ({ 
  onSimulate, 
  isLoading,
  addMessage
}) => {
  const [selectedScenario, setSelectedScenario] = useState("healthy");

  const handleSimulate = () => {
    const scenario = SCENARIOS.find(s => s.id === selectedScenario);
    if (scenario) {
      addMessage('info', `🚗 Simulating ${scenario.name}...`);
      onSimulate(selectedScenario);
    }
  };

  return (
    <Card className="glass-effect hover-lift border-slate-700/50">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center text-slate-100">
          <Zap className="w-5 h-5 mr-3 text-yellow-400" />
          Simulation Mode
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="grid grid-cols-1 gap-2">
            {SCENARIOS.map((scenario) => (
              <button
                key={scenario.id}
                onClick={() => setSelectedScenario(scenario.id)}
                disabled={isLoading}
                className={`p-3 text-left rounded-lg border transition-all duration-200 ${
                  selectedScenario === scenario.id
                    ? "bg-blue-500/20 border-blue-500/50 text-blue-100"
                    : "border-slate-600/50 text-slate-300 hover:bg-slate-800/50 hover:border-slate-500"
                }`}
              >
                <div className="font-medium text-sm">{scenario.name}</div>
                <div className="text-xs text-slate-400 mt-1">{scenario.description}</div>
              </button>
            ))}
          </div>
          
          <Button
            onClick={handleSimulate}
            disabled={isLoading}
            className="w-full h-12 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-medium transition-all duration-300 shadow-lg hover:shadow-xl"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Simulating...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5 mr-2" />
                Simulate Car
              </>
            )}
          </Button>
        </div>
        
        <div className="pt-3 border-t border-slate-700/30">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Wrench className="w-4 h-4" />
            <span>Test without hardware. Perfect for demos and development.</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};