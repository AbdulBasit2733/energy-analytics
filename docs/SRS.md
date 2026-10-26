# Software Requirements Specification

## 1. Introduction

This document specifies the functional and non-functional requirements for the UK Wind Forecast Accuracy Dashboard. Each requirement has a unique identifier for traceability.

## 2. Functional Requirements

### 2.1 Data Ingestion

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | The system shall fetch actual wind generation data from the Elexon BMRS FUELHH stream endpoint using `settlementDateFrom` and `settlementDateTo` parameters with `fuelType=WIND`. | P0 |
| FR-002 | The system shall fetch wind forecast data from the Elexon BMRS WINDFOR stream endpoint using `from`, `to`, `publishDateTimeFrom`, and `publishDateTimeTo` parameters. | P0 |
| FR-003 | The system shall parse FUELHH responses as flat JSON arrays containing fields: dataset, publishTime, startTime, settlementDate, settlementPeriod, fuelType, generation. | P0 |
| FR-004 | The system shall parse WINDFOR responses as flat JSON arrays containing fields: dataset, publishTime, startTime, generation. | P0 |
| FR-005 | The system shall treat all timestamps as UTC. | P0 |
| FR-006 | The system shall retry failed API requests up to 3 times with exponential backoff for 5xx errors and timeouts. | P1 |

### 2.2 Data Processing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-007 | The system shall aggregate FUELHH half-hourly records to hourly by averaging generation values for each pair of settlement periods within the same clock hour (floor startTime to nearest hour). | P0 |
| FR-008 | The system shall track how many half-hour records contributed to each hourly value (half_hour_count: 1 or 2). | P1 |
| FR-009 | The system shall select the day-ahead forecast using the D-1 cutoff rule: for each delivery date, find the WINDFOR forecast run with the latest publishTime that is strictly before the cutoff time. | P0 |
| FR-010 | The cutoff time shall default to 09:00 UTC on the day before delivery and be configurable via the FORECAST_CUTOFF_HOUR environment variable. | P0 |
| FR-011 | The system shall pair forecasts and actuals by matching on identical hour timestamps (inner join). Hours with missing data on either side shall be excluded from metrics. | P0 |
| FR-012 | The system shall not silently fill missing actual observations or treat missing forecasts as zero. | P0 |

### 2.3 Accuracy Metrics

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-013 | The system shall calculate MAE as mean(|forecast - actual|) in MW. | P0 |
| FR-014 | The system shall calculate RMSE as sqrt(mean((forecast - actual)²)) in MW. | P0 |
| FR-015 | The system shall calculate bias as mean(forecast - actual) in MW. Positive bias indicates over-forecasting. | P0 |
| FR-016 | The system shall calculate MAPE as mean(|forecast - actual| / actual) × 100, excluding hours where actual ≤ 1 MW. | P1 |
| FR-017 | The system shall calculate Pearson correlation coefficient between forecast and actual series. | P2 |
| FR-018 | The system shall report the number of paired hours used in each metric calculation. | P0 |

### 2.4 API Endpoints

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-019 | GET /api/health shall return cache status, dates cached, and total paired hours. | P0 |
| FR-020 | GET /api/dashboard/kpis shall return summary metrics for the full analysis period or a date range. | P0 |
| FR-021 | GET /api/timeseries shall return hourly forecast, actual, and error values, filterable by date or date range. | P0 |
| FR-022 | GET /api/forecast-history shall return all forecast runs for a given delivery date, indicating which was selected by the cutoff rule. | P0 |
| FR-023 | GET /api/accuracy/summary shall return overall accuracy metrics. | P0 |
| FR-024 | GET /api/accuracy/daily shall return per-day accuracy metrics. | P1 |
| FR-025 | GET /api/accuracy/error-distribution shall return histogram bins of forecast errors with configurable bin width. | P1 |
| FR-026 | GET /api/metadata shall return data source information, methodology description, and completeness statistics. | P1 |

### 2.5 Frontend

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-027 | The frontend shall display a Dashboard page with KPI cards and a full-month time series chart. | P0 |
| FR-028 | The frontend shall display a Time Series page with date selection and forecast vs actual chart. | P0 |
| FR-029 | The frontend shall display an Accuracy page with summary metrics, daily table, error distribution, and daily chart. | P0 |
| FR-030 | The frontend shall display a Procurement Insight page with bias analysis and worst-day table. | P1 |
| FR-031 | The frontend shall display a Methodology page explaining data sources, processing, and metrics. | P1 |
| FR-032 | The frontend shall show loading skeletons while data is fetching. | P0 |
| FR-033 | The frontend shall show error alerts when API requests fail. | P0 |
| FR-034 | The frontend shall show meaningful empty states when no data is available. | P1 |

## 3. Data Validation Rules

| Rule | Description |
|------|-------------|
| DV-001 | FUELHH `generation` values are integers in MW. Values may be negative for some fuel types but WIND generation is non-negative. |
| DV-002 | WINDFOR `generation` values are integers in MW, always non-negative. |
| DV-003 | All timestamps must parse as valid ISO 8601 datetime with UTC timezone. |
| DV-004 | Settlement periods must be integers 1–48. |
| DV-005 | Delivery dates must fall within the configured analysis period (January 2026 by default). |

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement |
|----|-------------|
| NFR-001 | Cache warm-up (initial data fetch) shall complete in under 2 minutes. |
| NFR-002 | All API endpoints shall respond in under 500ms when data is cached. |
| NFR-003 | The frontend shall render the dashboard page in under 3 seconds. |

### 4.2 Reliability

| ID | Requirement |
|----|-------------|
| NFR-004 | After initial cache warm-up, the application shall function without internet access (data served from disk cache). |
| NFR-005 | API errors from Elexon shall be retried with exponential backoff. |

### 4.3 Usability

| ID | Requirement |
|----|-------------|
| NFR-006 | The interface shall be responsive across desktop (1280px+), tablet (768px–1279px), and mobile (< 768px). |
| NFR-007 | Chart tooltips shall display values with units (MW). |
| NFR-008 | The sidebar navigation shall collapse to a hamburger menu on mobile. |

### 4.4 Security

| ID | Requirement |
|----|-------------|
| NFR-009 | No API keys or secrets shall be included in frontend source code. |
| NFR-010 | CORS shall be configured to allow only known frontend origins. |
| NFR-011 | All query parameters shall be validated via Pydantic models. |

## 5. External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Elexon BMRS API v1 | Current | Source for FUELHH and WINDFOR datasets |
| React | 19.3 | Frontend framework |
| Vite | 8.3 | Frontend build tool |
| FastAPI | 0.162+ | Backend framework |
| Pydantic | 2.9+ | Data validation |
| Recharts | 3.10+ | Charting library |
| TanStack Query | 5.x | Server-state management |
