import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ErrorDistributionBin } from "@/lib/api-client";
import { CHART_COLORS_HEX } from "@/lib/constants";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface Props {
  data?: ErrorDistributionBin[];
  loading?: boolean;
}

export function ErrorDistributionChart({ data, loading }: Props) {
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
          <CardTitle>Forecast Error Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            No data available.
          </div>
        </CardContent>
      </Card>
    );
  }

  const chartData = data.map((bin) => ({
    label: `${bin.bin_start >= 0 ? "+" : ""}${bin.bin_start}`,
    range: `${bin.bin_start} to ${bin.bin_end} MW`,
    count: bin.count,
    bin_start: bin.bin_start,  // Keep numeric value for ReferenceLine
    midpoint: (bin.bin_start + bin.bin_end) / 2,
  }));

  // Find the label that corresponds to zero (or closest bin containing zero)
  const zeroLabel = chartData.find(d => d.bin_start === 0)?.label ||
                    chartData.find(d => d.bin_start <= 0 && 0 < d.bin_start + 500)?.label;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Forecast Error Distribution</CardTitle>
        <CardDescription>
          Positive = over-forecast, Negative = under-forecast (MW)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 10 }}
              label={{ value: "Error (MW)", position: "bottom", offset: -5, style: { fontSize: 11 } }}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              label={{ value: "Hours", angle: -90, position: "insideLeft", offset: -5, style: { fontSize: 11 } }}
            />
            <Tooltip
              formatter={(value) => [`${value} hours`, "Count"]}
              labelFormatter={(label) => `Error bin: ${label} MW`}
            />
            {zeroLabel && (
              <ReferenceLine x={zeroLabel} stroke="#888" strokeDasharray="3 3" />
            )}
            <Bar
              dataKey="count"
              fill={CHART_COLORS_HEX.forecast}
              fillOpacity={0.8}
              radius={[2, 2, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
