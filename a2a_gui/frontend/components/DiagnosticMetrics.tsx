import type React from "react"
import { TrendingUp, TrendingDown, Minus, Gauge, Thermometer, Zap } from "lucide-react"
import { clsx } from "clsx"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface MetricData {
  label: string
  value: string
  unit: string
  status: "good" | "warning" | "critical"
  trend?: "up" | "down" | "stable"
  icon: React.ReactNode
}

interface DiagnosticMetricsProps {
  metrics?: MetricData[] // made optional
  isLoading?: boolean
}

export const DiagnosticMetrics: React.FC<DiagnosticMetricsProps> = ({
  metrics = [], // default to empty array to avoid runtime errors
  isLoading = false,
}) => {
  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="w-3 h-3" />
      case "down":
        return <TrendingDown className="w-3 h-3" />
      default:
        return <Minus className="w-3 h-3" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "good":
        return "text-green-400 bg-green-500/10 border-green-500/20"
      case "warning":
        return "text-yellow-400 bg-yellow-500/10 border-yellow-500/20"
      case "critical":
        return "text-red-400 bg-red-500/10 border-red-500/20"
      default:
        return "text-slate-400 bg-slate-500/10 border-slate-500/20"
    }
  }

  if (isLoading) {
    return (
      <Card className="glass-effect border-slate-700/50">
        <CardHeader>
          <CardTitle className="flex items-center text-slate-100">
            <Gauge className="w-5 h-5 mr-3 text-blue-400" />
            Live Diagnostics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 bg-slate-800/50 rounded skeleton" />
                <div className="h-6 bg-slate-800/50 rounded skeleton" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="glass-effect border-slate-700/50 hover-lift">
      <CardHeader>
        <CardTitle className="flex items-center text-slate-100">
          <Gauge className="w-5 h-5 mr-3 text-blue-400" />
          Live Diagnostics
        </CardTitle>
      </CardHeader>
      <CardContent>
        {metrics.length === 0 ? (
          <div className="text-sm text-slate-400 bg-slate-800/40 rounded-md p-4 border border-slate-700/50">
            No live metrics available yet. Connect and start a scan to see real-time data.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {metrics.map((metric, index) => (
              <div
                key={index}
                className={clsx(
                  "p-4 rounded-lg border transition-all duration-300 hover:shadow-lg",
                  getStatusColor(metric.status),
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {metric.icon}
                    <span className="text-sm font-medium">{metric.label}</span>
                  </div>
                  {metric.trend && (
                    <div className="flex items-center space-x-1 opacity-70">{getTrendIcon(metric.trend)}</div>
                  )}
                </div>

                <div className="flex items-baseline space-x-2">
                  <span className="text-2xl font-bold">{metric.value}</span>
                  <span className="text-sm opacity-70">{metric.unit}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Example usage component
export const LiveMetricsDisplay: React.FC = () => {
  const sampleMetrics: MetricData[] = [
    {
      label: "Engine RPM",
      value: "750",
      unit: "rpm",
      status: "good",
      trend: "stable",
      icon: <Gauge className="w-4 h-4" />,
    },
    {
      label: "Coolant Temp",
      value: "195",
      unit: "°F",
      status: "good",
      trend: "up",
      icon: <Thermometer className="w-4 h-4" />,
    },
    {
      label: "Battery Voltage",
      value: "12.6",
      unit: "V",
      status: "good",
      trend: "stable",
      icon: <Zap className="w-4 h-4" />,
    },
    {
      label: "Engine Load",
      value: "15",
      unit: "%",
      status: "good",
      trend: "down",
      icon: <Gauge className="w-4 h-4" />,
    },
  ]

  return <DiagnosticMetrics metrics={sampleMetrics} />
}
