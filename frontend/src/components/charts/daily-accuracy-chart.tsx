import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DailyAccuracy } from "@/lib/api-client";
import { CHART_COLORS_HEX } from "@/lib/constants";
import { formatDateShort } from "@/lib/utils";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface Props {
  data?: DailyAccuracy[];
  loading?: boolean;
}

export function DailyAccuracyChart({ data, loading }: Props) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!data?.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Daily Accuracy Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            No data available.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Daily Accuracy Metrics</CardTitle>
        <CardDescription>MAE and Bias by day — MW</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis
              dataKey="date"
              tickFormatter={formatDateShort}
              tick={{ fontSize: 10 }}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              label={{ value: "MW", angle: -90, position: "insideLeft", offset: -5, style: { fontSize: 11 } }}
            />
            <Tooltip
              labelFormatter={(label) => formatDateShort(String(label))}
              formatter={(value, name) => [
                `${Number(value).toLocaleString()} MW`,
                String(name),
              ]}
            />
            <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
            <Bar
              dataKey="mae"
              name="MAE"
              fill={CHART_COLORS_HEX.forecast}
              fillOpacity={0.6}
              radius={[2, 2, 0, 0]}
            />
            <Line
              type="monotone"
              dataKey="bias"
              name="Bias"
              stroke={CHART_COLORS_HEX.bias}
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
