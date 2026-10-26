import {
  Area,
  Brush,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TimeSeriesPoint } from "@/lib/api-client";
import { CHART_COLORS_HEX } from "@/lib/constants";
import { formatDateTime, formatHour } from "@/lib/utils";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const DEFAULT_BRUSH_DAYS = 7;
const DEFAULT_BRUSH_HOURS = DEFAULT_BRUSH_DAYS * 24;

interface ForecastVsActualChartProps {
  data?: TimeSeriesPoint[];
  loading?: boolean;
  title?: string;
  showBrush?: boolean;
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-card p-3 shadow-md text-sm">
      <p className="font-medium mb-1.5">{formatDateTime(label)}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center gap-2">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-muted-foreground">{entry.name}:</span>
          <span className="font-mono font-medium">
            {entry.value != null && isFinite(entry.value)
              ? `${entry.value.toLocaleString()} MW`
              : "—"}
          </span>
        </div>
      ))}
    </div>
  );
}

export function ForecastVsActualChart({
  data,
  loading,
  title = "Forecast vs Actual Wind Generation",
  showBrush = true,
}: ForecastVsActualChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-64" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[400px] w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!data?.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[300px] text-muted-foreground">
            No data available for the selected period.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>
          Hourly comparison — MW (megawatts)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={420}>
          <ComposedChart
            data={data}
            margin={{ top: 5, right: 20, bottom: 5, left: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis
              dataKey="hour"
              tickFormatter={formatHour}
              tick={{ fontSize: 11 }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 11 }}
              tickFormatter={(v: number | null) => {
                if (v == null || !isFinite(v)) return "—";
                return `${(v / 1000).toFixed(0)}k`;
              }}
              label={{
                value: "MW",
                angle: -90,
                position: "insideLeft",
                offset: -5,
                style: { fontSize: 11, fill: "#888" },
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
            />
            <Area
              type="monotone"
              dataKey="error_mw"
              name="Error"
              fill={CHART_COLORS_HEX.error}
              fillOpacity={0.1}
              stroke="none"
            />
            <Line
              type="monotone"
              dataKey="actual_mw"
              name="Actual"
              stroke={CHART_COLORS_HEX.actual}
              strokeWidth={2}
              dot={false}
              connectNulls={false}
            />
            <Line
              type="monotone"
              dataKey="forecast_mw"
              name="Forecast"
              stroke={CHART_COLORS_HEX.forecast}
              strokeWidth={2}
              strokeDasharray="6 3"
              dot={false}
              connectNulls={false}
            />
            {showBrush && data.length > 48 && (
              <Brush
                dataKey="hour"
                height={30}
                stroke={CHART_COLORS_HEX.forecast}
                tickFormatter={formatHour}
                startIndex={0}
                endIndex={Math.min(DEFAULT_BRUSH_HOURS - 1, data.length - 1)}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
