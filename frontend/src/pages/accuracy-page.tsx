import { useState } from "react";
import { DailyAccuracyChart } from "@/components/charts/daily-accuracy-chart";
import { ErrorDistributionChart } from "@/components/charts/error-distribution-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CompactDateSelector } from "@/components/ui/date-range-selector";
import { Skeleton } from "@/components/ui/skeleton";
import { useAccuracyDaily, useAccuracySummary, useErrorDistribution } from "@/hooks/use-accuracy";
import { formatMW, formatPercent } from "@/lib/utils";

export function AccuracyPage() {
  const [dateRange, setDateRange] = useState<{ from?: string; to?: string }>({});

  const summary = useAccuracySummary(dateRange.from, dateRange.to);
  const daily = useAccuracyDaily(dateRange.from, dateRange.to);
  const distribution = useErrorDistribution(500, dateRange.from, dateRange.to);

  const handleDateRangeChange = (from: string, to: string) => {
    setDateRange({ from, to });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Forecast Accuracy Analysis</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Quantitative metrics comparing forecast vs actual wind generation
          </p>
        </div>
        <div className="min-w-[240px]">
          <CompactDateSelector onRangeChange={handleDateRangeChange} />
        </div>
      </div>

      {summary.isLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      ) : summary.data ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard label="MAE" value={formatMW(summary.data.mae)} desc="Mean Absolute Error" />
          <MetricCard label="RMSE" value={formatMW(summary.data.rmse)} desc="Root Mean Square Error" />
          <MetricCard label="Bias" value={formatMW(summary.data.bias)} desc={summary.data.bias > 0 ? "Over-forecast tendency" : "Under-forecast tendency"} />
          <MetricCard label="MAPE" value={summary.data.mape != null ? formatPercent(summary.data.mape) : "N/A"} desc="Mean Absolute % Error" />
          <MetricCard label="Max Over-forecast" value={formatMW(summary.data.max_overforecast)} desc="Largest positive error" />
          <MetricCard label="Max Under-forecast" value={formatMW(summary.data.max_underforecast)} desc="Largest negative error" />
          <MetricCard label="Correlation" value={summary.data.correlation != null ? summary.data.correlation.toFixed(4) : "N/A"} desc="Pearson coefficient" />
          <MetricCard label="Paired Hours" value={String(summary.data.paired_hours)} desc="Hours with both forecast & actual" />
        </div>
      ) : null}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <ErrorDistributionChart data={distribution.data} loading={distribution.isLoading} />
        <DailyAccuracyChart data={daily.data} loading={daily.isLoading} />
      </div>

      {daily.data && daily.data.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Daily Metrics Table</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3 font-medium text-muted-foreground">Date</th>
                    <th className="text-right py-2 px-3 font-medium text-muted-foreground">MAE (MW)</th>
                    <th className="text-right py-2 px-3 font-medium text-muted-foreground">RMSE (MW)</th>
                    <th className="text-right py-2 px-3 font-medium text-muted-foreground">Bias (MW)</th>
                    <th className="text-right py-2 px-3 font-medium text-muted-foreground">Hours</th>
                  </tr>
                </thead>
                <tbody>
                  {daily.data.map((row) => (
                    <tr key={row.date} className="border-b last:border-0">
                      <td className="py-2 px-3 font-mono text-xs">{row.date}</td>
                      <td className="py-2 px-3 text-right font-mono">{row.mae.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono">{row.rmse.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono">{row.bias.toLocaleString()}</td>
                      <td className="py-2 px-3 text-right font-mono">{row.paired_hours}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function MetricCard({ label, value, desc }: { label: string; value: string; desc: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-xs text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className="text-xl font-semibold font-mono mt-1">{value}</p>
        <p className="text-xs text-muted-foreground mt-0.5">{desc}</p>
      </CardContent>
    </Card>
  );
}
