# Data Dictionary

## Source Datasets

### FUELHH — Actual Generation by Fuel Type

**Endpoint:** `GET https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream`

**Fields:**

| Field | Type | Description | Example | Units |
|-------|------|-------------|---------|-------|
| `dataset` | string | Dataset identifier | `"FUELHH"` | N/A |
| `publishTime` | ISO datetime (UTC) | When record was published | `"2026-01-15T00:30:00Z"` | N/A |
| `startTime` | ISO datetime (UTC) | Start of settlement period | `"2026-01-15T00:00:00Z"` | N/A |
| `settlementDate` | date (YYYY-MM-DD) | GB settlement date | `"2026-01-15"` | N/A |
| `settlementPeriod` | integer (1-48) | Half-hour period index | `1` | N/A |
| `fuelType` | string | Fuel type code | `"WIND"` | N/A |
| `generation` | integer | Generated power | `14969` | MW |

**API Parameters:**
- `settlementDateFrom` (YYYY-MM-DD) — Start date filter
- `settlementDateTo` (YYYY-MM-DD) — End date filter
- `fuelType` — Filter by fuel type (e.g., `WIND`)
- **Note:** Uses `settlementDateFrom`/`settlementDateTo`, NOT `from`/`to`

**Temporal Resolution:** 30 minutes (half-hourly). 48 periods per day.

---

### WINDFOR — Wind Generation Forecast

**Endpoint:** `GET https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream`

**Fields:**

| Field | Type | Description | Example | Units |
|-------|------|-------------|---------|-------|
| `dataset` | string | Dataset identifier | `"WINDFOR"` | N/A |
| `publishTime` | ISO datetime (UTC) | When forecast was issued | `"2026-01-14T07:30:00Z"` | N/A |
| `startTime` | ISO datetime (UTC) | Target forecast hour | `"2026-01-15T00:00:00Z"` | N/A |
| `generation` | integer | Forecast power | `15823` | MW |

**API Parameters:**
- `from` (ISO datetime) — Filter startTime ≥ value
- `to` (ISO datetime) — Filter startTime ≤ value
- `publishDateTimeFrom` (ISO datetime) — Filter publishTime ≥ value
- `publishDateTimeTo` (ISO datetime) — Filter publishTime ≤ value

**Temporal Resolution:** 1 hour (hourly). ~24 periods per forecast run, multiple runs per day.

---

## Derived Fields

### HourlyActual
Aggregated from FUELHH by averaging two consecutive half-hours.

| Field | Type | Description | Units |
|-------|------|-------------|-------|
| `hour` | datetime (UTC) | Hour timestamp (floor of startTime) | N/A |
| `generation_mw` | float | Average of 2 half-hours | MW |
| `half_hour_count` | int | Number of half-hours included (1 or 2) | count |

**Aggregation Rule:**
```
hour = floor(startTime to nearest hour)
generation_mw = average(values within that hour)
```

### HourlyForecast
Selected from WINDFOR based on D-1 cutoff.

| Field | Type | Description | Units |
|-------|------|-------------|-------|
| `hour` | datetime (UTC) | Target forecast hour | N/A |
| `generation_mw` | float | Forecast power | MW |
| `publish_time` | datetime (UTC) | When this forecast was issued | N/A |

### ForecastActualPair
Matched hourly forecast and actual.

| Field | Type | Description | Units |
|-------|------|-------------|-------|
| `hour` | datetime (UTC) | Matched hour | N/A |
| `forecast_mw` | float | Forecast generation | MW |
| `actual_mw` | float | Actual generation | MW |
| `error_mw` | float | forecast - actual | MW |
| `abs_error_mw` | float | \|forecast - actual\| | MW |
| `error_pct` | float or null | (forecast - actual) / actual × 100 | % |

**Sign Convention:**
- Positive `error_mw` = forecast exceeded actual (over-forecast)
- Negative `error_mw` = forecast below actual (under-forecast)

**Null Handling:**
- `error_pct` is `null` when `actual_mw` ≤ 1 MW (to avoid division by near-zero)

---

## Timezone Rules

- All timestamps are **UTC** (ISO 8601 with `Z` suffix)
- January 2026 is **GMT (UTC+0)** — no British Summer Time offset
- No timezone conversion needed for January data
- BST applies March 29 – October 25, 2026 (not relevant to this analysis)

---

## Data Validation

### FUELHH
- `settlementPeriod` must be 1-48
- `generation` can be negative (interconnector exports, pumped storage)
- `fuelType` = `"WIND"` filter applied
- 48 records expected per day for complete data

### WINDFOR
- `generation` is always positive (wind output only)
- ~24 records per forecast run (one per hour)
- Multiple forecast runs per day (~6-10 runs)
- `publishTime` < `startTime` always (forecasts precede delivery)

### Pairing
- Only hours where both forecast AND actual exist are paired
- Missing data is not imputed or filled
- Completeness reported as % of expected hourly pairs

---

## Example Records

### FUELHH (Actual)
```json
{
  "dataset": "FUELHH",
  "publishTime": "2026-01-15T00:30:00Z",
  "startTime": "2026-01-15T00:00:00Z",
  "settlementDate": "2026-01-15",
  "settlementPeriod": 1,
  "fuelType": "WIND",
  "generation": 14969
}
```

### WINDFOR (Forecast)
```json
{
  "dataset": "WINDFOR",
  "publishTime": "2026-01-14T07:30:00Z",
  "startTime": "2026-01-15T00:00:00Z",
  "generation": 15823
}
```

### HourlyActual (Derived)
```json
{
  "hour": "2026-01-15T00:00:00Z",
  "generation_mw": 14456.5,
  "half_hour_count": 2
}
```

### ForecastActualPair (Derived)
```json
{
  "hour": "2026-01-15T00:00:00Z",
  "forecast_mw": 15834.0,
  "actual_mw": 14456.5,
  "error_mw": 1377.5,
  "abs_error_mw": 1377.5,
  "error_pct": 9.53
}
```
