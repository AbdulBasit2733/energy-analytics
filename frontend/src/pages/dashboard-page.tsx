import { useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CompactDateSelector } from "@/components/ui/date-range-selector";
import { ForecastVsActualChart } from "@/components/charts/forecast-vs-actual-chart";
import { KPIGrid } from "@/components/dashboard/kpi-grid";
import { useDashboardKPIs } from "@/hooks/use-dashboard";
import { useTimeseries } from "@/hooks/use-timeseries";

export function DashboardPage() {
  const [dateRange, setDateRange] = useState<{ from?: string; to?: string }>({});

  const kpis = useDashboardKPIs(dateRange.from, dateRange.to);
  const timeseries = useTimeseries({ from: dateRange.from, to: dateRange.to });

  const handleDateRangeChange = (from: string, to: string) => {
    setDateRange({ from, to });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Dashboard Overview</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Wind forecast accuracy summary for January 2026
          </p>
        </div>
        <div className="min-w-[240px]">
          <CompactDateSelector onRangeChange={handleDateRangeChange} />
        </div>
      </div>

      {kpis.error && (
        <Alert variant="destructive">
          <AlertTitle>Failed to load dashboard</AlertTitle>
          <AlertDescription>
            {kpis.error instanceof Error ? kpis.error.message : "Unknown error"}
          </AlertDescription>
        </Alert>
      )}

      <KPIGrid data={kpis.data} loading={kpis.isLoading} />

      {timeseries.error && (
        <Alert variant="destructive">
          <AlertTitle>Failed to load time series</AlertTitle>
          <AlertDescription>
            {timeseries.error instanceof Error ? timeseries.error.message : "Unknown error"}
          </AlertDescription>
        </Alert>
      )}

      <ForecastVsActualChart
        data={timeseries.data}
        loading={timeseries.isLoading}
        title="Forecast vs Actual — Full Month"
        showBrush
      />
    </div>
  );
}
