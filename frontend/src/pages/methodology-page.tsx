import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useMetadata } from "@/hooks/use-dashboard";

export function MethodologyPage() {
  const { data, isLoading } = useMetadata();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-40" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold tracking-tight">Data & Methodology</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Transparency about data sources, processing, and assumptions
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Data Sources</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-relaxed">
          <p>
            All data is sourced from the <strong>Elexon Balancing Mechanism Reporting Service (BMRS)</strong>,
            the official source for GB electricity market data.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
            <div className="rounded-md border p-3">
              <p className="font-medium">Actual Generation</p>
              <p className="text-muted-foreground mt-1">
                Dataset: <code className="text-xs bg-muted px-1 py-0.5 rounded">FUELHH</code><br />
                Resolution: {data?.resolution_actual || "Half-hourly (30 min)"}<br />
                Filter: fuelType = WIND
              </p>
            </div>
            <div className="rounded-md border p-3">
              <p className="font-medium">Forecast Generation</p>
              <p className="text-muted-foreground mt-1">
                Dataset: <code className="text-xs bg-muted px-1 py-0.5 rounded">WINDFOR</code><br />
                Resolution: {data?.resolution_forecast || "Hourly"}<br />
                Multiple forecast runs per day
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Resolution Mismatch</CardTitle>
        </CardHeader>
        <CardContent className="text-sm leading-relaxed space-y-2">
          <p>
            FUELHH provides actual wind generation at <strong>half-hourly</strong> intervals
            (48 periods per day), while WINDFOR provides forecasts at <strong>hourly</strong> intervals
            (24 periods per day).
          </p>
          <p>
            <strong>Aggregation method:</strong> {data?.aggregation_method || "Two consecutive FUELHH half-hourly values are averaged to produce one hourly value for comparison with WINDFOR."}
          </p>
          <p className="text-muted-foreground">
            For example, settlement periods 1 (00:00–00:30) and 2 (00:30–01:00) are averaged to
            produce the hourly actual for the 00:00 hour, which is then compared with the WINDFOR
            forecast for that same hour.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Forecast Selection Logic</CardTitle>
        </CardHeader>
        <CardContent className="text-sm leading-relaxed space-y-2">
          <p>
            {data?.forecast_cutoff_description || "The day-ahead forecast cutoff is at 09:00 UTC on D-1."}
          </p>
          <p>
            For each delivery date, the system identifies the most recent WINDFOR forecast run
            published <strong>before</strong> the cutoff. This ensures the comparison uses only
            information that was available when the procurement decision needed to be made.
          </p>
          <div className="rounded-md bg-muted/50 p-3 mt-2 font-mono text-xs">
            <p>Example for delivery date 2026-01-15:</p>
            <p>Cutoff = 2026-01-14 09:00 UTC</p>
            <p>Selected = latest WINDFOR publishTime before cutoff</p>
            <p>Typically ~07:30 UTC on 2026-01-14</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Accuracy Metrics</CardTitle>
        </CardHeader>
        <CardContent className="text-sm leading-relaxed">
          <div className="space-y-3">
            <div>
              <p className="font-medium">MAE (Mean Absolute Error)</p>
              <p className="text-muted-foreground">
                Average of |forecast - actual| across all matched hourly pairs. Units: MW.
                Measures typical error magnitude regardless of direction.
              </p>
            </div>
            <div>
              <p className="font-medium">RMSE (Root Mean Square Error)</p>
              <p className="text-muted-foreground">
                Square root of the mean of squared errors. Units: MW.
                Penalises large errors more heavily than MAE. RMSE &ge; MAE always.
              </p>
            </div>
            <div>
              <p className="font-medium">Bias (Mean Error)</p>
              <p className="text-muted-foreground">
                Average of (forecast - actual). Units: MW.
                {" "}{data?.bias_convention || "Positive = forecast exceeded actual (over-forecast)."}
              </p>
            </div>
            <div>
              <p className="font-medium">MAPE (Mean Absolute Percentage Error)</p>
              <p className="text-muted-foreground">
                Average of |forecast - actual| / actual &times; 100. Units: %.
                Hours where actual generation &le; 1 MW are excluded to avoid division by near-zero.
                MAPE can be misleading for wind data due to periods of very low generation.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {data && (
        <Card>
          <CardHeader>
            <CardTitle>Data Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-muted-foreground">Analysis period:</span>
                <span className="ml-2 font-mono">{data.analysis_period}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Timezone:</span>
                <span className="ml-2 font-mono">{data.timezone}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Units:</span>
                <span className="ml-2 font-mono">{data.units}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Delivery dates:</span>
                <span className="ml-2 font-mono">{data.total_delivery_dates}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Hourly pairs:</span>
                <span className="ml-2 font-mono">{data.total_hourly_pairs}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Completeness:</span>
                <span className="ml-2 font-mono">{data.data_completeness_pct}%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
