import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ForecastHistoryResponse } from "@/lib/api-client";
import { CHART_COLORS_HEX } from "@/lib/constants";
import { formatDateTime, formatHour } from "@/lib/utils";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface Props {
  data?: ForecastHistoryResponse;
  loading?: boolean;
}

const RUN_COLORS = [
  "#94a3b8",
  "#a1a1aa",
  "#9ca3af",
  "#a3a3a3",
  "#b4bcd0",
  "#8b95a8",
  "#7d8a9e",
  "#6b7b92",
];

export function ForecastHistoryChart({ data, loading }: Props) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-64" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[400px] w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!data?.runs?.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Forecast Publication History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            Select a delivery date to view forecast history.
          </div>
        </CardContent>
      </Card>
    );
  }

  const allHours = new Set<string>();
  for (const run of data.runs) {
    for (const f of run.forecasts) {
      allHours.add(f.hour);
    }
  }
  const sortedHours = [...allHours].sort();

  const chartData = sortedHours.map((hour) => {
    const point: Record<string, any> = { hour };
    for (let i = 0; i < data.runs.length; i++) {
      const run = data.runs[i];
      const match = run.forecasts.find((f) => f.hour === hour);
      point[`run_${i}`] = match?.forecast_mw ?? null;
    }
    return point;
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Forecast Publication History</CardTitle>
        <CardDescription>
          Delivery: {data.delivery_date} | Cutoff: {formatDateTime(data.cutoff_time)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis dataKey="hour" tickFormatter={formatHour} tick={{ fontSize: 11 }} />
            <YAxis
              tick={{ fontSize: 11 }}
              tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
              label={{ value: "MW", angle: -90, position: "insideLeft", offset: -5, style: { fontSize: 11 } }}
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                return (
                  <div className="rounded-lg border border-border bg-card p-3 shadow-md text-sm max-h-60 overflow-y-auto">
                    <p className="font-medium mb-1.5">{formatDateTime(String(label))}</p>
                    {payload.map((entry: any, i: number) => {
                      if (entry.value == null) return null;
                      return (
                        <div key={i} className="flex items-center gap-2">
                          <span
                            className="inline-block h-2 w-2 rounded-full"
                            style={{ backgroundColor: entry.color }}
                          />
                          <span className="text-muted-foreground text-xs">
                            {entry.name}:
                          </span>
                          <span className="font-mono text-xs">
                            {entry.value?.toLocaleString()} MW
                          </span>
                        </div>
                      );
                    })}
                  </div>
                );
              }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            {data.runs.map((run, i) => (
              <Line
                key={i}
                type="monotone"
                dataKey={`run_${i}`}
                name={formatDateTime(run.publish_time)}
                stroke={
                  run.is_selected
                    ? CHART_COLORS_HEX.forecast
                    : RUN_COLORS[i % RUN_COLORS.length]
                }
                strokeWidth={run.is_selected ? 3 : 1}
                strokeDasharray={run.is_selected ? undefined : "4 2"}
                dot={false}
                connectNulls={false}
                opacity={run.is_selected ? 1 : 0.5}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
        <div className="mt-3 text-xs text-muted-foreground">
          <strong>Selected forecast:</strong>{" "}
          {data.runs.find((r) => r.is_selected)
            ? formatDateTime(data.runs.find((r) => r.is_selected)!.publish_time)
            : "None"}{" "}
          (latest before cutoff)
        </div>
      </CardContent>
    </Card>
  );
}
