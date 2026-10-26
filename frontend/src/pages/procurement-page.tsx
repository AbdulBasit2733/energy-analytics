import { AlertTriangle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { useAccuracyDaily, useAccuracySummary } from "@/hooks/use-accuracy";
import { formatMW } from "@/lib/utils";

export function ProcurementPage() {
  const summary = useAccuracySummary();
  const daily = useAccuracyDaily();

  if (summary.isLoading || daily.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-40" />
        <Skeleton className="h-40" />
      </div>
    );
  }

  const metrics = summary.data;
  const dailyData = daily.data;

  const worstDays = dailyData
    ? [...dailyData].sort((a, b) => b.mae - a.mae).slice(0, 5)
    : [];

  const biasDirection = metrics
    ? metrics.bias > 0
      ? "positive"
      : metrics.bias < 0
        ? "negative"
        : "neutral"
    : "neutral";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold tracking-tight">Procurement Insight</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Implications of forecast errors for day-ahead electricity procurement
        </p>
      </div>

      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          These insights are indicative only. Wind forecast error alone does not determine
          the utility's required power purchase. Consumer demand, other generation sources,
          and interconnector flows are outside the scope of this analysis.
        </AlertDescription>
      </Alert>

      {metrics && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Forecast Bias Direction</CardTitle>
              <CardDescription>
                Sign convention: Positive = forecast exceeded actual generation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-bold font-mono">
                  {formatMW(metrics.bias)}
                </span>
                <span className="text-sm text-muted-foreground">mean bias</span>
              </div>
              <p className="text-sm leading-relaxed">
                {biasDirection === "positive" ? (
                  <>
                    The BMRS wind forecast consistently <strong>over-predicted</strong> wind
                    generation by an average of {formatMW(Math.abs(metrics.bias))} per hour.
                    This means actual wind output was lower than expected. In procurement terms,
                    the utility would have expected more wind on the system than materialised,
                    potentially leading to higher-than-expected balancing costs when conventional
                    generation was needed to fill the shortfall.
                  </>
                ) : biasDirection === "negative" ? (
                  <>
                    The BMRS wind forecast consistently <strong>under-predicted</strong> wind
                    generation by an average of {formatMW(Math.abs(metrics.bias))} per hour.
                    This means actual wind output was higher than expected. The utility would
                    have over-procured conventional generation, potentially at a cost premium,
                    when wind could have covered more demand.
                  </>
                ) : (
                  <>
                    The forecast shows no significant systematic bias. Over- and under-predictions
                    roughly cancel out across the analysis period.
                  </>
                )}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Forecast Uncertainty</CardTitle>
              <CardDescription>RMSE as a proxy for forecast risk</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-bold font-mono">
                  {formatMW(metrics.rmse)}
                </span>
                <span className="text-sm text-muted-foreground">RMSE</span>
              </div>
              <p className="text-sm leading-relaxed">
                The Root Mean Square Error of {formatMW(metrics.rmse)} indicates the typical
                magnitude of hourly forecast errors, with heavier weighting on large deviations.
                A procurement analyst should budget for wind generation to deviate from forecast
                by approximately this amount in any given hour. The maximum single-hour
                over-forecast was {formatMW(metrics.max_overforecast)} and the maximum
                under-forecast was {formatMW(Math.abs(metrics.max_underforecast))}.
              </p>
            </CardContent>
          </Card>

          {worstDays.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Highest Error Days</CardTitle>
                <CardDescription>Top 5 days by Mean Absolute Error</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground">Date</th>
                        <th className="text-right py-2 px-3 font-medium text-muted-foreground">MAE (MW)</th>
                        <th className="text-right py-2 px-3 font-medium text-muted-foreground">Bias (MW)</th>
                        <th className="text-left py-2 px-3 font-medium text-muted-foreground">Direction</th>
                      </tr>
                    </thead>
                    <tbody>
                      {worstDays.map((day) => (
                        <tr key={day.date} className="border-b last:border-0">
                          <td className="py-2 px-3 font-mono text-xs">{day.date}</td>
                          <td className="py-2 px-3 text-right font-mono">{day.mae.toLocaleString()}</td>
                          <td className="py-2 px-3 text-right font-mono">{day.bias.toLocaleString()}</td>
                          <td className="py-2 px-3 text-xs">
                            {day.bias > 0 ? "Over-forecast" : "Under-forecast"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
