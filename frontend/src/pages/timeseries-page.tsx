import { useState } from "react";
import { ForecastVsActualChart } from "@/components/charts/forecast-vs-actual-chart";
import { ForecastHistoryChart } from "@/components/charts/forecast-history-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useForecastHistory, useTimeseries } from "@/hooks/use-timeseries";
import { formatDateTime } from "@/lib/utils";

const JAN_DATES = Array.from({ length: 31 }, (_, i) => {
  const d = i + 1;
  return `2026-01-${String(d).padStart(2, "0")}`;
});

export function TimeseriesPage() {
  const [selectedDate, setSelectedDate] = useState("2026-01-15");
  const timeseries = useTimeseries({ date: selectedDate });
  const forecastHistory = useForecastHistory(selectedDate);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Time Series Analysis</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Hourly forecast vs actual comparison
          </p>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="date-select" className="text-sm text-muted-foreground">
            Delivery date:
          </label>
          <select
            id="date-select"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="rounded-md border border-input bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          >
            {JAN_DATES.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>
      </div>

      <ForecastVsActualChart
        data={timeseries.data}
        loading={timeseries.isLoading}
        title={`Forecast vs Actual — ${selectedDate}`}
        showBrush={false}
      />

      <ForecastHistoryChart
        data={forecastHistory.data}
        loading={forecastHistory.isLoading}
      />

      {forecastHistory.data && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Forecast Runs Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3 font-medium text-muted-foreground">Published</th>
                    <th className="text-right py-2 px-3 font-medium text-muted-foreground">Points</th>
                    <th className="text-center py-2 px-3 font-medium text-muted-foreground">Selected</th>
                  </tr>
                </thead>
                <tbody>
                  {forecastHistory.data.runs.map((run, i) => (
                    <tr
                      key={i}
                      className={`border-b last:border-0 ${run.is_selected ? "bg-primary/5 font-medium" : ""}`}
                    >
                      <td className="py-2 px-3 font-mono text-xs">
                        {formatDateTime(run.publish_time)}
                      </td>
                      <td className="py-2 px-3 text-right font-mono">
                        {run.forecasts.length}
                      </td>
                      <td className="py-2 px-3 text-center">
                        {run.is_selected ? (
                          <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                            Selected
                          </span>
                        ) : (
                          ""
                        )}
                      </td>
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
