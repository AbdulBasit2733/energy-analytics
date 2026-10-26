# Glossary

## Purpose

This glossary defines domain-specific terms, acronyms, and technical concepts used throughout the project documentation and dashboard interface.

---

## Energy Market Terms

### Actual Generation
The measured electrical power output from wind turbines, reported by Elexon in the FUELHH dataset. Units: megawatts (MW).

### Balancing Mechanism
The system operated by National Grid ESO to balance electricity supply and demand in real-time across Great Britain.

### BMRS (Balancing Mechanism Reporting Service)
Elexon's public data service providing near-real-time and historical electricity market data for Great Britain. API: https://data.elexon.co.uk/bmrs/api/v1

### BSC (Balancing and Settlement Code)
The legal framework governing electricity balancing and settlement in Great Britain. Administered by Elexon.

### BST (British Summer Time)
UTC+1 timezone used in the UK from last Sunday in March to last Sunday in October. Not applicable to January analysis (GMT applies).

### Curtailment
Intentional reduction of wind generation below available capacity, typically due to grid constraints or negative pricing.

### Day-Ahead Market
Electricity trading market where power is bought and sold for delivery the following day. GB day-ahead auction operated by N2EX (Nord Pool).

### Delivery Date
The calendar date when electricity is physically delivered (generated/consumed). Distinct from trading date.

### D-1 (Day-Ahead)
One day before delivery. Example: For January 15 delivery, D-1 = January 14.

### Elexon
The Balancing and Settlement Code Company Ltd, responsible for balancing and settlement administration in GB electricity market.

### FUELHH Dataset
Elexon BMRS dataset providing actual half-hourly generation by fuel type (WIND, CCGT, NUCLEAR, etc.). "FUEL" = fuel type, "HH" = half-hourly.

### Gate Closure
Deadline for submitting day-ahead market bids. N2EX GB day-ahead gate closure: ~09:00–09:30 UK time on D-1.

### GMT (Greenwich Mean Time)
UTC+0 timezone used in UK during winter months (late October to late March). January is always GMT.

### National Grid ESO (Electricity System Operator)
Company responsible for operating GB electricity transmission system and balancing supply/demand.

### N2EX (Nord Pool Exchange)
GB day-ahead and intraday electricity auction market, operated by Nord Pool.

### Procurement
The process of purchasing electricity in wholesale markets to meet demand forecasts.

### Settlement Period (SP)
30-minute time block used in GB electricity settlement. 48 settlement periods per day (numbered 1-48). SP1 = 00:00–00:30, SP48 = 23:30–24:00.

### Settlement Date
The GB market date for settlement purposes. May differ from calendar date near midnight due to settlement period numbering.

### Transmission Constraints
Grid infrastructure limitations that restrict power flow, sometimes requiring curtailment of generation.

### WINDFOR Dataset
Elexon BMRS dataset providing hourly wind generation forecasts. "WIND" = wind generation, "FOR" = forecast.

---

## Forecast Accuracy Terms

### Absolute Error
The magnitude of forecast error, ignoring direction. Formula: `|forecast - actual|`. Units: MW.

### Bias (Mean Error)
The average signed error across all forecasts. Indicates systematic over/under-forecasting tendency.
- **Positive bias:** Forecasts tend to over-predict (forecast > actual on average)
- **Negative bias:** Forecasts tend to under-predict (forecast < actual on average)
- **Zero bias:** No systematic tendency (errors cancel out)
Units: MW.

### Correlation (Pearson)
Statistical measure of linear relationship strength between forecast and actual values. Range: -1 to +1. Values near +1 indicate strong positive relationship.

### Cutoff Time
Deadline by which a forecast must be published to be operationally useful. This project uses 09:00 UTC on D-1.

### Error
The difference between forecast and actual. Formula: `forecast - actual`.
- **Positive error:** Over-forecast (forecast > actual)
- **Negative error:** Under-forecast (forecast < actual)
Units: MW.

### Forecast Horizon
Time interval between forecast publication and target delivery time. This project analyzes day-ahead horizon (~15-33 hours ahead).

### Forecast Run
A complete set of forecasts issued at a single publication time. WINDFOR typically has 6-10 runs per day, each covering ~72 hours ahead.

### MAE (Mean Absolute Error)
Average magnitude of forecast errors. Formula: `(1/N) × Σ|forecast - actual|`. Primary accuracy metric. Units: MW.

### MAPE (Mean Absolute Percentage Error)
Average forecast error as percentage of actual generation. Formula: `(100/N) × Σ(|forecast - actual| / actual)`. Sensitive to low actuals; this project excludes hours where actual ≤1 MW. Units: %.

### Over-Forecast
Forecast value exceeds actual generation (positive error). Example: Forecast 15,000 MW, actual 14,000 MW → over-forecast by 1,000 MW.

### Paired Hours
Hours where both forecast and actual generation data exist. Only paired hours included in accuracy metrics. January 2026: 744 paired hours (100% completeness).

### Publish Time
UTC timestamp when a forecast was issued/published. Distinct from forecast target time (startTime).

### RMSE (Root Mean Square Error)
Average forecast error with heavier penalty for large errors. Formula: `sqrt((1/N) × Σ(forecast - actual)²)`. RMSE ≥ MAE always. Units: MW.

### Squared Error
Error raised to power of 2. Used in RMSE calculation. Penalizes large errors more than MAE.

### Under-Forecast
Forecast value below actual generation (negative error). Example: Forecast 14,000 MW, actual 15,000 MW → under-forecast by 1,000 MW.

---

## Technical Terms

### API (Application Programming Interface)
Software interface for accessing data or services programmatically. This project uses Elexon BMRS API (REST).

### CORS (Cross-Origin Resource Sharing)
Browser security mechanism controlling which domains can access API resources. Backend must allow frontend domain in CORS configuration.

### Cache
Temporary storage of data to improve performance and reduce API calls. This project uses two-tier cache: in-memory + file-based JSON.

### CSV (Comma-Separated Values)
Plain-text file format for tabular data. Used for exporting data tables.

### Dashboard
Web interface displaying key metrics and visualizations in a single view.

### Docker
Platform for containerizing applications. This project uses Docker Compose to orchestrate backend + frontend services.

### Endpoint
Specific URL path in an API. Example: `/api/health`, `/api/dashboard/kpis`.

### FastAPI
Modern Python web framework for building APIs. Used for backend.

### Git
Version control system for tracking code changes.

### HTTPX
Async Python HTTP client library. Used for calling Elexon API with retry logic.

### JSON (JavaScript Object Notation)
Lightweight text format for data interchange. Used for API responses and cache files.

### JWT (JSON Web Token)
Security token format for authentication. Not implemented in v1.0 (no authentication).

### KPI (Key Performance Indicator)
Metric used to evaluate success. Dashboard displays 6 KPIs: avg actual, avg forecast, MAE, RMSE, bias, completeness.

### Nginx
Web server software. Used to serve frontend static files and proxy API requests.

### NumPy
Python library for numerical computing. Used for vectorized metrics calculations.

### Pandas
Python library for data manipulation. Used for time-series aggregation.

### Pydantic
Python library for data validation using type hints. Used for API request/response schemas.

### React
JavaScript library for building user interfaces. Used for frontend.

### REST (Representational State Transfer)
Architectural style for APIs. Elexon BMRS and backend APIs are RESTful.

### shadcn/ui
React component library (CLI-based, not npm package). Provides accessible UI primitives.

### SSL/TLS (Secure Sockets Layer / Transport Layer Security)
Cryptographic protocols for secure communication. Production deployment uses HTTPS (TLS).

### SPA (Single-Page Application)
Web app that loads once and updates content dynamically without full page reloads. This dashboard is an SPA.

### Tailwind CSS
Utility-first CSS framework. Version 4 uses CSS-first configuration.

### TanStack Query (React Query)
React library for data fetching, caching, and synchronization. Used for API calls in frontend.

### TypeScript
Typed superset of JavaScript. Used for frontend code.

### UTC (Coordinated Universal Time)
Primary time standard. All timestamps in this project are UTC. January UK time = UTC (GMT).

### Uvicorn
ASGI server for running FastAPI applications.

### Vite
Modern build tool for frontend development. Faster than Webpack.

### Recharts
React charting library built on D3. Used for all dashboard visualizations.

---

## Statistical Terms

### Confidence Interval
Range of values that likely contains true population parameter. Not implemented in v1.0.

### Mean
Average value. Formula: `(1/N) × Σx`.

### Median
Middle value when data sorted. More robust to outliers than mean.

### Outlier
Data point significantly different from others. Often indicates unusual event (e.g., storm, equipment failure).

### Population
Complete set of data points. This project analyzes population (all 744 hours), not sample.

### Sample
Subset of population. Not applicable here (full population analyzed).

### Standard Deviation
Measure of data spread around mean. Formula: `sqrt((1/N) × Σ(x - mean)²)`.

### Variance
Squared standard deviation. Measure of data variability.

---

## Abbreviations

| Abbreviation | Full Term |
|--------------|-----------|
| AA | Accessibility Level AA (WCAG 2.2) |
| BMRS | Balancing Mechanism Reporting Service |
| BSC | Balancing and Settlement Code |
| BST | British Summer Time |
| CCGT | Combined Cycle Gas Turbine |
| CI/CD | Continuous Integration / Continuous Deployment |
| CLS | Cumulative Layout Shift (Core Web Vital) |
| CORS | Cross-Origin Resource Sharing |
| CPU | Central Processing Unit |
| CSV | Comma-Separated Values |
| D-1 | Day-Ahead (one day before delivery) |
| ECS | Elastic Container Service (AWS) |
| EFS | Elastic File System (AWS) |
| ESO | Electricity System Operator |
| FID | First Input Delay (Core Web Vital) |
| GB | Great Britain |
| GMT | Greenwich Mean Time |
| HH | Half-Hourly |
| HTTPS | Hypertext Transfer Protocol Secure |
| ISO | International Organization for Standardization |
| JSON | JavaScript Object Notation |
| JWT | JSON Web Token |
| KPI | Key Performance Indicator |
| LCP | Largest Contentful Paint (Core Web Vital) |
| MAE | Mean Absolute Error |
| MAPE | Mean Absolute Percentage Error |
| MB | Megabyte |
| MW | Megawatt |
| MWh | Megawatt-hour |
| N2EX | Nord Pool Exchange |
| PDF | Portable Document Format |
| PNG | Portable Network Graphics |
| REST | Representational State Transfer |
| RMSE | Root Mean Square Error |
| RTL | React Testing Library |
| SPA | Single-Page Application |
| SP | Settlement Period |
| SQL | Structured Query Language |
| SSL | Secure Sockets Layer |
| SVG | Scalable Vector Graphics |
| TLS | Transport Layer Security |
| TTFB | Time to First Byte |
| UI | User Interface |
| URL | Uniform Resource Locator |
| UTC | Coordinated Universal Time |
| UX | User Experience |
| WCAG | Web Content Accessibility Guidelines |

---

## Units

| Unit | Full Name | Description |
|------|-----------|-------------|
| MW | Megawatt | Power unit (1 MW = 1,000,000 watts) |
| MWh | Megawatt-hour | Energy unit (1 MWh = 1 MW sustained for 1 hour) |
| GW | Gigawatt | Power unit (1 GW = 1,000 MW) |
| GWh | Gigawatt-hour | Energy unit (1 GWh = 1,000 MWh) |
| kB | Kilobyte | Data size (1 kB = 1,024 bytes) |
| MB | Megabyte | Data size (1 MB = 1,024 kB) |
| ms | Millisecond | Time unit (1 ms = 0.001 seconds) |
| % | Percent | Proportion out of 100 |

---

## Formula Reference

### MAE (Mean Absolute Error)
```
MAE = (1/N) × Σ|forecast - actual|
```

### RMSE (Root Mean Square Error)
```
RMSE = sqrt((1/N) × Σ(forecast - actual)²)
```

### Bias (Mean Error)
```
Bias = (1/N) × Σ(forecast - actual)
```

### MAPE (Mean Absolute Percentage Error)
```
MAPE = (100/N) × Σ(|forecast - actual| / actual)
[where actual > threshold, typically 1 MW]
```

### Correlation (Pearson)
```
r = cov(forecast, actual) / (σ_forecast × σ_actual)
```

### Hourly Aggregation (FUELHH)
```
hourly_actual = (half_hour_1 + half_hour_2) / 2
```

---

## See Also

- **[DATA_DICTIONARY.md](DATA_DICTIONARY.md)** — Field definitions for FUELHH and WINDFOR datasets
- **[FORECAST_METHODOLOGY.md](FORECAST_METHODOLOGY.md)** — Detailed methodology for forecast selection and metrics
- **[API.md](API.md)** — API endpoint reference
- **[USER_GUIDE.md](USER_GUIDE.md)** — End-user documentation

---

## Document Version

**Version:** 1.0  
**Last Updated:** 2026-10-26  
