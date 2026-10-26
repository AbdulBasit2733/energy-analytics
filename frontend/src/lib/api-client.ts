import { API_BASE } from "./constants";

async function fetchJSON<T>(
  path: string,
  params?: Record<string, string>
): Promise<T> {
  const url = new URL(`${API_BASE}${path}`, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      // Don't drop falsy values like 0 or empty string
      if (v !== undefined && v !== null) {
        url.searchParams.set(k, String(v));
      }
    });
  }

  // Add 30-second timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const res = await fetch(url.toString(), {
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`API ${res.status}: ${text || res.statusText}`);
    }

    // Safely parse JSON with error handling
    try {
      return await res.json();
    } catch (error) {
      const text = await res.text().catch(() => "");
      throw new Error(`Invalid JSON response: ${text.substring(0, 500)}`);
    }
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error("Request timeout - server took too long to respond");
    }
    throw error;
  }
}

export interface DashboardKPIs {
  period: string;
  total_actual_mwh: number;
  total_forecast_mwh: number;
  avg_actual_mw: number;
  avg_forecast_mw: number;
  mae_mw: number;
  rmse_mw: number;
  bias_mw: number;
  mape_pct: number | null;
  data_completeness_pct: number;
  hours_analyzed: number;
  latest_forecast_publish_time: string | null;
}

export interface TimeSeriesPoint {
  hour: string;
  forecast_mw: number | null;
  actual_mw: number | null;
  error_mw: number | null;
}

export interface ForecastRun {
  publish_time: string;
  is_selected: boolean;
  forecasts: TimeSeriesPoint[];
}

export interface ForecastHistoryResponse {
  delivery_date: string;
  cutoff_time: string;
  runs: ForecastRun[];
}

export interface AccuracyMetrics {
  mae: number;
  rmse: number;
  mape: number | null;
  bias: number;
  max_overforecast: number;
  max_underforecast: number;
  correlation: number | null;
  paired_hours: number;
}

export interface DailyAccuracy {
  date: string;
  mae: number;
  rmse: number;
  bias: number;
  paired_hours: number;
}

export interface ErrorDistributionBin {
  bin_start: number;
  bin_end: number;
  count: number;
}

export interface MetadataResponse {
  data_source: string;
  api_base_url: string;
  analysis_period: string;
  forecast_cutoff_description: string;
  forecast_cutoff_hour_utc: number;
  resolution_actual: string;
  resolution_forecast: string;
  aggregation_method: string;
  units: string;
  timezone: string;
  total_delivery_dates: number;
  total_hourly_pairs: number;
  data_completeness_pct: number;
  bias_convention: string;
}

export interface HealthResponse {
  status: string;
  cache_loaded: boolean;
  dates_cached: number;
  total_pairs: number;
}

export const api = {
  getHealth: () => fetchJSON<HealthResponse>("/health"),
  getDashboardKPIs: (from?: string, to?: string) =>
    fetchJSON<DashboardKPIs>("/dashboard/kpis", {
      ...(from && { from }),
      ...(to && { to }),
    }),
  getTimeseries: (params?: { date?: string; from?: string; to?: string }) =>
    fetchJSON<TimeSeriesPoint[]>("/timeseries", params),
  getForecastHistory: (date: string) =>
    fetchJSON<ForecastHistoryResponse>("/forecast-history", { date }),
  getAccuracySummary: (from?: string, to?: string) =>
    fetchJSON<AccuracyMetrics>("/accuracy/summary", {
      ...(from && { from }),
      ...(to && { to }),
    }),
  getAccuracyDaily: (from?: string, to?: string) =>
    fetchJSON<DailyAccuracy[]>("/accuracy/daily", {
      ...(from && { from }),
      ...(to && { to }),
    }),
  getErrorDistribution: (binWidth?: number, from?: string, to?: string) =>
    fetchJSON<ErrorDistributionBin[]>("/accuracy/error-distribution", {
      ...(binWidth && { bin_width: String(binWidth) }),
      ...(from && { from }),
      ...(to && { to }),
    }),
  getMetadata: () => fetchJSON<MetadataResponse>("/metadata"),
};
