import {
  Activity,
  BarChart3,
  CheckCircle2,
  TrendingDown,
  TrendingUp,
  Zap,
} from "lucide-react";
import type { DashboardKPIs } from "@/lib/api-client";
import { formatMW, formatPercent } from "@/lib/utils";
import { KPICard } from "./kpi-card";

interface KPIGridProps {
  data?: DashboardKPIs;
  loading?: boolean;
}

export function KPIGrid({ data, loading }: KPIGridProps) {
  if (loading || !data) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <KPICard key={i} label="" value="" loading />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <KPICard
        label="Avg Actual Wind"
        value={formatMW(data.avg_actual_mw)}
        subtitle={`${data.hours_analyzed} hourly observations`}
        icon={<Zap className="h-4 w-4" />}
      />
      <KPICard
        label="Avg Forecast Wind"
        value={formatMW(data.avg_forecast_mw)}
        subtitle="Day-ahead forecast (D-1 09:00 UTC)"
        icon={<TrendingUp className="h-4 w-4" />}
      />
      <KPICard
        label="MAE"
        value={formatMW(data.mae_mw)}
        subtitle="Mean Absolute Error"
        icon={<Activity className="h-4 w-4" />}
      />
      <KPICard
        label="RMSE"
        value={formatMW(data.rmse_mw)}
        subtitle="Root Mean Square Error"
        icon={<BarChart3 className="h-4 w-4" />}
      />
      <KPICard
        label="Forecast Bias"
        value={formatMW(data.bias_mw)}
        subtitle={
          data.bias_mw > 0
            ? "Forecast tends to over-predict"
            : data.bias_mw < 0
              ? "Forecast tends to under-predict"
              : "No systematic bias"
        }
        icon={<TrendingDown className="h-4 w-4" />}
        trend={
          Math.abs(data.bias_mw) > 500
            ? "negative"
            : Math.abs(data.bias_mw) < 100
              ? "positive"
              : "neutral"
        }
      />
      <KPICard
        label="Data Completeness"
        value={formatPercent(data.data_completeness_pct)}
        subtitle={`${data.hours_analyzed} of 744 expected hours`}
        icon={<CheckCircle2 className="h-4 w-4" />}
        trend={
          data.data_completeness_pct >= 95
            ? "positive"
            : data.data_completeness_pct >= 80
              ? "neutral"
              : "negative"
        }
      />
    </div>
  );
}
