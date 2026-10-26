# API Reference

Base URL: `http://localhost:8000/api` (local) or `https://<backend-domain>/api` (production)

All endpoints return JSON. All timestamps are UTC (ISO 8601).

## Health Check

### GET /api/health

Check backend status and cache readiness.

**Response:**
```json
{
  "status": "ok",
  "cache_loaded": true,
  "dates_cached": 31,
  "total_pairs": 744
}
```

---

## Dashboard

### GET /api/dashboard/kpis

Aggregated KPI metrics for the analysis period.

**Query Parameters:**
- `start` (optional): Start date filter (YYYY-MM-DD)
- `end` (optional): End date filter (YYYY-MM-DD)

**Response:**
```json
{
  "period": "January 2026",
  "total_actual_mwh": 10891234.5,
  "total_forecast_mwh": 11023456.7,
  "avg_actual_mw": 14637.0,
  "avg_forecast_mw": 14815.0,
  "mae_mw": 892.5,
  "rmse_mw": 1123.4,
  "bias_mw": 178.0,
  "mape_pct": 6.12,
  "data_completeness_pct": 100.0,
  "hours_analyzed": 744,
  "latest_forecast_publish_time": "2026-01-31T07:30:00Z"
}
```

### GET /api/metadata

Data source and methodology information.

**Response:**
```json
{
  "data_source": "Elexon BMRS (Balancing Mechanism Reporting Service)",
  "api_base_url": "https://data.elexon.co.uk/bmrs/api/v1",
  "analysis_period": "2026-01",
  "forecast_cutoff_description": "Day-ahead forecast cutoff at 09:00 UTC on D-1...",
  "forecast_cutoff_hour_utc": 9,
  "resolution_actual": "Half-hourly (30 min) — FUELHH dataset",
  "resolution_forecast": "Hourly — WINDFOR dataset",
  "aggregation_method": "FUELHH half-hourly values averaged to hourly...",
  "units": "MW (megawatts)",
  "timezone": "UTC (January is GMT, so UTC = UK local time)",
  "total_delivery_dates": 31,
  "total_hourly_pairs": 744,
  "data_completeness_pct": 100.0,
  "bias_convention": "Positive bias = forecast exceeded actual (over-forecast)"
}
```

---

## Time Series

### GET /api/timeseries

Hourly forecast vs actual comparison.

**Query Parameters:**
- `date` (optional): Single date (YYYY-MM-DD)
- `from` (optional): Start date (YYYY-MM-DD)
- `to` (optional): End date (YYYY-MM-DD)

**Response:**
```json
[
  {
    "hour": "2026-01-15T00:00:00Z",
    "forecast_mw": 15834.0,
    "actual_mw": 14456.5,
    "error_mw": 1377.5
  },
  ...
]
```

**Notes:**
- `forecast_mw`, `actual_mw`, `error_mw` can be `null` if data unavailable
- Default: all January 2026 (744 points)
- Use `date` for single-day view (24 points)

---

## Forecast History

### GET /api/forecast-history

All forecast runs for a specific delivery date.

**Query Parameters:**
- `date` (required): Delivery date (YYYY-MM-DD)

**Response:**
```json
{
  "delivery_date": "2026-01-15",
  "cutoff_time": "2026-01-14T09:00:00Z",
  "runs": [
    {
      "publish_time": "2026-01-14T07:30:00Z",
      "is_selected": true,
      "forecasts": [
        {
          "hour": "2026-01-15T00:00:00Z",
          "forecast_mw": 15834.0,
          "actual_mw": null,
          "error_mw": null
        },
        ...
      ]
    },
    ...
  ]
}
```

**Notes:**
- `is_selected` = `true` for the forecast run selected at D-1 cutoff
- Each run contains ≤24 forecasts for the delivery date

---

## Accuracy Analysis

### GET /api/accuracy/summary

Overall accuracy metrics.

**Query Parameters:**
- `from` (optional): Start date filter
- `to` (optional): End date filter

**Response:**
```json
{
  "mae": 892.5,
  "rmse": 1123.4,
  "mape": 6.12,
  "bias": 178.0,
  "max_overforecast": 3245.6,
  "max_underforecast": -2891.2,
  "correlation": 0.9823,
  "paired_hours": 744
}
```

### GET /api/accuracy/daily

Per-day accuracy breakdown.

**Query Parameters:**
- `from` (optional): Start date filter
- `to` (optional): End date filter

**Response:**
```json
[
  {
    "date": "2026-01-15",
    "mae": 875.2,
    "rmse": 1089.3,
    "bias": 192.5,
    "paired_hours": 24
  },
  ...
]
```

### GET /api/accuracy/error-distribution

Error distribution histogram.

**Query Parameters:**
- `bin_width` (optional): Bin width in MW (default: 500)
- `from` (optional): Start date filter
- `to` (optional): End date filter

**Response:**
```json
[
  {
    "bin_start": -3000.0,
    "bin_end": -2500.0,
    "count": 3
  },
  {
    "bin_start": -2500.0,
    "bin_end": -2000.0,
    "count": 12
  },
  ...
]
```

---

## Error Handling

### Status Codes

- `200` — Success
- `400` — Invalid query parameters
- `404` — Resource not found (e.g., no data for requested date)
- `422` — Validation error (Pydantic)
- `500` — Internal server error

### Error Response Format

```json
{
  "detail": "No forecast data for 2026-01-32"
}
```

---

## CORS Configuration

Allowed origins (configurable via `CORS_ORIGINS` env var):
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Docker frontend)
- Production frontend domain

---

## Rate Limiting

No rate limiting on backend. Upstream Elexon API has no documented limits. Backend caches all January 2026 data after first fetch — subsequent requests serve from memory.

---

## OpenAPI Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
