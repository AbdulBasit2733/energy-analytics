# Product Requirements Document

## 1. Product Overview

The **UK Wind Forecast Accuracy Dashboard** is a web application that enables electricity procurement analysts at a UK energy utility to evaluate the accuracy of national wind generation forecasts provided by Elexon BMRS. By comparing day-ahead wind forecasts against actual half-hourly wind generation data for January 2026, the dashboard helps analysts understand forecast reliability and its implications for wholesale electricity procurement decisions.

## 2. Problem Statement

UK energy utilities purchase electricity from the wholesale day-ahead market. Wind generation — the largest renewable source on the GB grid — is inherently variable and depends on weather. Procurement decisions must be made before delivery, using forecasts that may prove inaccurate.

Without a clear view of forecast accuracy, procurement analysts cannot:

- Quantify the magnitude and direction of forecast errors.
- Identify days when forecasts were particularly unreliable.
- Adjust procurement strategies to account for systematic forecast bias.
- Communicate forecast risk to trading desks and senior management.

## 3. Target Users

| Persona | Role | Needs |
|---------|------|-------|
| Procurement Analyst | Buys electricity on the day-ahead market | Understand wind forecast accuracy to inform purchasing volume |
| Trading Desk Manager | Oversees energy trading operations | Assess forecast risk exposure and systematic bias |
| Energy Data Analyst | Supports procurement with quantitative analysis | Access to raw metrics, export-friendly data views |

## 4. Business Goals

1. Provide a single dashboard where analysts can assess January 2026 wind forecast accuracy.
2. Quantify forecast errors using industry-standard metrics (MAE, RMSE, bias, MAPE).
3. Show which forecast was available at the time of the procurement decision, not the latest available.
4. Enable data-driven discussion about forecast risk in procurement meetings.

## 5. Scope

### In Scope

- National-level UK wind generation data from Elexon BMRS.
- FUELHH dataset (actual half-hourly wind generation, filtered for fuelType=WIND).
- WINDFOR dataset (hourly wind generation forecasts with publication timestamps).
- Delivery periods in January 2026 (2026-01-01 through 2026-01-31).
- Day-ahead forecast cutoff at 09:00 UTC on D-1 (configurable).
- React frontend with TypeScript.
- Python FastAPI backend.
- Docker containerisation.

### Out of Scope

- Real-time streaming or live market data.
- Consumer demand forecasting.
- Non-wind fuel types.
- Multi-month or multi-year analysis.
- Third-party weather data providers.
- Automated trading recommendations.
- User authentication (the dashboard is read-only).

## 6. Functional Requirements

### Feature 1: Dashboard Overview

Display summary KPI cards for the selected period:

- Average actual wind generation (MW).
- Average forecast wind generation (MW).
- MAE, RMSE, bias (MW).
- MAPE (%) where valid.
- Data completeness percentage.
- Number of hourly observations analysed.

### Feature 2: Forecast vs Actual Chart

Time-series chart comparing hourly forecast and actual wind generation:

- Actual line (solid green), forecast line (dashed blue).
- Error area shading.
- Brush control for zoom/pan across the full month.
- Tooltips with hour, forecast, actual, and error values.
- Loading, empty, and error states.

### Feature 3: Forecast Publication History

For a selected delivery date, display all forecast runs:

- Each run's publication time.
- Which run was selected by the D-1 cutoff rule.
- Visual comparison of how forecasts evolved over time.
- Table listing runs with point counts and selected flag.

### Feature 4: Forecast Accuracy Analysis

Detailed accuracy metrics and visualisations:

- Summary metrics card grid (MAE, RMSE, bias, MAPE, correlation, max errors).
- Error distribution histogram.
- Daily MAE and bias chart over January.
- Daily metrics table (sortable).

### Feature 5: Procurement Insight

Interpretive analysis based on calculated metrics:

- Forecast bias direction and its procurement implications.
- RMSE as a proxy for forecast uncertainty.
- Top 5 highest-error days.
- Caveat that wind error alone does not determine procurement needs.

### Feature 6: Data Transparency

Methodology and data source information:

- Data sources (FUELHH, WINDFOR) with Elexon attribution.
- Resolution mismatch explanation (half-hourly vs hourly).
- Forecast selection logic description.
- Metric formulas and definitions.
- Data completeness summary.

## 7. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Cache warm-up time | < 2 minutes on first start |
| API response time | < 500ms (from cache) |
| Frontend build | < 5 seconds |
| Browser support | Modern browsers (Chrome, Firefox, Safari, Edge) |
| Responsive design | Desktop, tablet, and mobile layouts |
| Accessibility | Semantic HTML, keyboard navigation, sufficient contrast |

## 8. User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-01 | As a procurement analyst, I want to see average forecast error for January so I can assess overall forecast reliability. | P0 |
| US-02 | As an analyst, I want to compare forecast and actual wind generation on a chart so I can visually identify error patterns. | P0 |
| US-03 | As an analyst, I want to see which forecast was available before the auction closed so I know decisions were based on realistic information. | P0 |
| US-04 | As a trading manager, I want daily accuracy metrics so I can identify particularly unreliable forecast days. | P1 |
| US-05 | As an analyst, I want to understand forecast bias direction so I can anticipate whether wind is likely to be over- or under-predicted. | P1 |
| US-06 | As a data analyst, I want to see data source and methodology details so I can validate the analysis. | P1 |
| US-07 | As an analyst, I want to zoom into specific date ranges on the chart so I can investigate interesting periods. | P2 |
| US-08 | As a user, I want the dashboard to load quickly so I can use it during procurement meetings. | P1 |

## 9. Acceptance Criteria

1. The dashboard displays real Elexon data for January 2026, not synthetic data.
2. Forecast selection uses only forecasts published before the documented cutoff time.
3. MAE, RMSE, and bias are calculated on matched hourly pairs only.
4. The half-hourly to hourly aggregation is documented and verifiable.
5. The interface is responsive and works on desktop, tablet, and mobile.
6. All API endpoints return valid JSON matching documented schemas.
7. Backend tests pass (46/46 as of initial implementation).
8. Frontend builds without TypeScript errors.
9. Docker Compose starts both services successfully.

## 10. Risks and Assumptions

| Risk/Assumption | Impact | Mitigation |
|-----------------|--------|------------|
| Elexon API may be temporarily unavailable | Cannot fetch data | Two-tier cache (in-memory + file) eliminates API dependency after first successful fetch |
| WINDFOR forecasts may not cover all 24 hours for every delivery date | Reduced completeness | Track and display paired_hours count; calculate metrics only on available pairs |
| FUELHH uses `settlementDateFrom`/`To` not `from`/`to` | Silent data fetch failure | Verified via live API testing; parameter names hardcoded correctly |
| Day-ahead cutoff time may vary by auction operator | Wrong forecast selected | Cutoff hour is configurable via environment variable |
| MAPE is unreliable when actual wind is near zero | Misleading percentage errors | Exclude hours with actual ≤ 1 MW from MAPE; document limitation |

## 11. Success Criteria

The project is successful when:

1. A procurement analyst can open the dashboard and understand January 2026 forecast accuracy within 2 minutes.
2. All six features are functional with real Elexon data.
3. The methodology is transparent and documented.
4. A technical reviewer can understand the architecture and run the tests.
5. The application runs locally via Docker Compose with a single command.
