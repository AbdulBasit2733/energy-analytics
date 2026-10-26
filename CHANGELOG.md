# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (2026-10-26)
- **Multi-Month Date Picker**: Support for all 12 months of 2026 (Jan-Dec), quarterly ranges (Q1-Q4), full year, and custom date selection
- **Custom Date Range Input**: Native HTML5 date pickers for selecting any arbitrary start/end dates
- **Preset Quick Select**: 17 predefined ranges (12 months + 4 quarters + full year + custom)
- **Two-Mode Selector**: Compact version switches between preset dropdown and custom date inputs
- **Dynamic Filtering**: All KPIs, charts, and metrics update instantly when date range changes
- **TanStack Query Integration**: Date range parameters passed to all API hooks, automatic cache per range
- **Backend Ready**: API endpoints support filtering by any date range via `from`/`to` parameters

### Fixed (2026-10-26)

**Previous Fixes:**
- API parameter mismatch - frontend sent `start`/`end` but backend expected `from`/`to` (date filtering was completely broken)
- Missing error handling for timeseries API failures (infinite spinner on error)
- No 404 page for invalid URLs (blank screen instead of helpful message)
- Zero reference line missing on error distribution chart (ReferenceLine didn't match string labels)
- Hardcoded API URL prevented production deployment (no environment variable support)
- No request timeout (fetch waited forever if backend hung)

**Critical Bugs Fixed (Phase 1):**
- **BUG #1**: Cache eviction logic - counted dates instead of months (would evict after 12 days not 12 months)
- **BUG #2**: No date range validation (backend) - allowed start > end, returned empty data instead of HTTP 400 error
- **BUG #3**: No config validation - invalid `forecast_cutoff_hour`, `analysis_month`, or `analysis_year` caused startup crashes
- **BUG #4**: Bin width validation missing - values ≤0 or negative caused infinite loop and server hang
- **BUG #5**: API client dropped falsy parameters - `if (v)` dropped `0`, `""`, preventing valid edge-case requests

**High-Priority Bugs Fixed (Phase 2):**
- **BUG #6**: Frontend date range validation - added checks to prevent start > end before API calls
- **BUG #7**: JSON parsing error handling - malformed responses now show helpful error messages
- **BUG #8**: Timeseries conflicting parameters - using both `date` and `from`/`to` now returns HTTP 400
- **BUG #10**: Chart Y-axis formatter - handles null/undefined/NaN values defensively
- **BUG #11**: Magic number in brush - extracted constant `DEFAULT_BRUSH_DAYS = 7` for maintainability
- **BUG #12**: Index bounds checking - CompactDateSelector validates array access before use
- **BUG #14**: Empty values guard - data_processor skips empty hourly groups defensively
- **BUG #21**: Tooltip value safety - checks isFinite() before formatting to prevent NaN display
- **Production Issues**: Memory leaks (HTTPX client, unbounded cache, infinite TanStack Query cache), connection pool limits, Docker resource limits, silent API failures

### Technical Improvements (2026-10-26)
- Added 30-second request timeout with AbortController
- Configurable API URL via `VITE_API_URL` environment variable
- HTTPX client cleanup in FastAPI lifespan shutdown
- Cache eviction policy (12-month limit) with `_evict_old_cache()` method
- Connection pool limits (max 20 connections, 5 keepalive)
- Docker resource limits (1GB memory, 1 CPU core)
- TanStack Query cache tuning (24h staleTime, 2h gcTime)
- Zero-handling consistency across accuracy metrics (>1.0 MW threshold)
- Failed API dates tracking with CRITICAL logging

### Documentation (2026-10-26)
- Added `docs/DATE_PICKER_FEATURE.md` - Complete feature documentation with use cases, technical implementation, video demo talking points
- Added `docs/MULTI_MONTH_SETUP.md` - Guide for enabling multiple months in backend (config, testing, troubleshooting, performance)
- Added `docs/FRONTEND_BUG_FIXES.md` - Detailed bug report (6 bugs fixed, impact analysis, testing, verification)
- Added `docs/PRODUCTION_AUDIT.md` - Memory leak analysis, scalability issues, Docker optimization
- Added `docs/VALIDATION_REPORT.md` - Pre-deployment validation, build verification, test results
- Added `deliverables/*.docx` - 8 Word documents generated from Markdown sources

### Known Limitations (2026-10-26)
- **Backend Data**: Currently only January 2026 is pre-cached. To enable other months (October, etc.), update `CACHE_MONTHS` environment variable in `backend/.env` and restart. See [docs/MULTI_MONTH_SETUP.md](docs/MULTI_MONTH_SETUP.md) for full guide.
- **On-Demand Fetching**: Backend does not yet fetch uncached months automatically. Selecting October without configuring it will return empty data.

### Planned
- CSV export functionality for tables
- PNG export for charts
- Dark mode support
- Touch-friendly zoom controls for mobile

## [1.0.0] - 2026-10-26

### Added
- **Dashboard Page**: Overview with 6 KPI cards (avg actual, avg forecast, MAE, RMSE, bias, completeness)
- **Time Series Page**: Interactive Recharts visualization with forecast vs actual comparison, error area, and brush zoom control
- **Accuracy Analysis Page**: Overall metrics summary, daily metrics table (sortable), error distribution histogram
- **Procurement Insights Page**: Over/under-forecast analysis, top error days, risk assessment based on RMSE
- **Data Transparency Page**: Accordion sections explaining data sources, methodology, cutoff logic, metrics, completeness, caveats
- **Backend API**: FastAPI with 8 endpoints (health, dashboard/kpis, metadata, timeseries, forecast-history, accuracy/summary, accuracy/daily, accuracy/error-distribution)
- **Elexon BMRS Integration**: HTTPX async client with retry logic for FUELHH (actuals) and WINDFOR (forecasts) datasets
- **Two-Tier Caching**: In-memory dict + file-based JSON cache for zero-API-dependency after first startup
- **Forecast Selection Logic**: D-1 cutoff at 09:00 UTC, selects latest forecast run before cutoff
- **Hourly Aggregation**: Averages two consecutive FUELHH half-hours into one hourly value for comparison with WINDFOR
- **Accuracy Metrics**: MAE, RMSE, MAPE (excludes near-zero actuals), Bias, Correlation (Pearson), Max over/under-forecast
- **Docker Support**: docker-compose.yml with backend (FastAPI + Uvicorn) and frontend (Vite build + Nginx) services
- **Testing**: 46 pytest backend tests covering aggregation, forecast selection, metrics calculation, edge cases
- **Documentation**: 15+ Markdown files (PRD, SRS, ARCHITECTURE, DATA_DICTIONARY, FORECAST_METHODOLOGY, API, TESTING, DEPLOYMENT, SECURITY, USER_GUIDE, DECISIONS, ASSUMPTIONS_AND_LIMITATIONS, GLOSSARY, KNOWN_ISSUES, DEMO_SCRIPT, UI_UX_DESIGN_SYSTEM)
- **UI/UX Design System**: Documented color palette (oklch), typography (Inter + JetBrains Mono), accessibility compliance (WCAG AA), responsive breakpoints
- **Accessibility**: WCAG 2.2 AA compliance (4.5:1 contrast, keyboard navigation, ARIA labels, screen reader support)
- **Responsive Design**: Mobile-first layout, sidebar collapses to hamburger on <1024px, KPI grid adapts 1/2/3 columns
- **Type Safety**: TypeScript strict mode (frontend), Pydantic v2 (backend) with 0 compilation errors
- **CORS Configuration**: Specific origins only, GET methods, credentials allowed for future auth
- **Health Check Endpoint**: `/api/health` returns cache status, dates cached, total pairs
- **OpenAPI Documentation**: Auto-generated at `/docs` (Swagger UI) and `/redoc`

### Technical Stack
- **Frontend**: React 19.3, Vite 8.3.4, Tailwind CSS v4.3 (CSS-first config), shadcn/ui CLI v4, Recharts 3, TanStack Query 5, React Router 7
- **Backend**: Python 3.12, FastAPI 0.162.0, Pydantic v2, HTTPX (async), Pandas, NumPy, pytest
- **Deployment**: Docker 24+, docker-compose, Nginx (frontend static serve + reverse proxy)

### Data Coverage
- **Analysis Period**: January 2026 (31 days, 744 hours)
- **Data Completeness**: 100% (744/744 hourly pairs present)
- **Data Source**: Elexon BMRS API (FUELHH actuals half-hourly + WINDFOR forecasts hourly)
- **Forecast Cutoff**: 09:00 UTC on D-1 (configurable via `FORECAST_CUTOFF_HOUR`)

### Integration Validation
- Real Elexon API tested with January 2026 data
- Cache warm successful (31 dates, 744 pairs)
- Jan 15 forecast selection verified (publishTime 07:30 UTC on Jan 14, before 09:00 cutoff)
- All metrics cross-checked with manual calculations

### Known Limitations (v1.0)
- Single month only (January 2026), no date range filters
- Light mode only (no dark mode)
- No CSV/PDF export functionality
- No user authentication or role-based access
- Mobile brush zoom component hidden (touch controls not optimized)
- Static historical data (no real-time updates)

---

## [0.2.0] - 2026-10-25 (Development Milestone)

### Added
- Backend core services: elexon_client, data_processor, forecast_selector, accuracy_metrics, cache_manager
- API routers: dashboard, timeseries, forecast_history, accuracy, health
- Frontend components: KPIGrid, ForecastVsActualChart, DailyMetricsTable, ErrorDistributionChart, AppLayout
- Test suite: 46 pytest tests (data_processor, forecast_selector, accuracy_metrics)
- Tailwind v4 CSS-first configuration with theme tokens in index.css

### Fixed
- Elexon API parameter discovery: FUELHH uses `settlementDateFrom`/`To`, not `from`/`to`
- Recharts tooltip type warnings: Cast label to String(label)
- TypeScript baseUrl deprecation: Added ignoreDeprecations: "6.0"
- Vitest config error: Moved test config from vite.config.ts to separate vitest.config.ts

---

## [0.1.0] - 2026-10-24 (Project Scaffolding)

### Added
- Project structure: backend/, frontend/, docs/, deliverables/
- .gitignore, .env.example, docker-compose.yml, CLAUDE.md
- Backend: pyproject.toml, requirements.txt, Dockerfile, app/main.py skeleton
- Frontend: Vite + React setup, package.json, vite.config.ts, Dockerfile, nginx.conf
- Initial documentation: PRD.md, SRS.md, ARCHITECTURE.md, PROJECT_PLAN.md

---

## Version History Summary

| Version | Date | Key Features |
|---------|------|--------------|
| 1.0.0 | 2026-10-26 | Full dashboard, 8 API endpoints, 46 tests, 15+ docs, Docker deployment |
| 0.2.0 | 2026-10-25 | Backend services, frontend components, test suite |
| 0.1.0 | 2026-10-24 | Project scaffolding, initial setup |

---

## Upgrade Notes

### Migrating from Development to v1.0

**Backend:**
- Set `CORS_ORIGINS` environment variable with frontend domain
- Mount persistent volume at `/app/cache` for cache persistence
- Set `DEBUG=false` for production

**Frontend:**
- Set `VITE_API_URL` to production backend URL
- Build static assets: `npm run build`
- Serve via Nginx or host on Vercel/Railway

**Docker:**
- `docker compose up --build` for first deployment
- Persistent cache volume configured in docker-compose.yml

---

## Future Roadmap

### v1.1 (Planned Q1 2027)
- Date range filters (dashboard, time series, accuracy pages)
- CSV export for tables
- PNG export for charts
- API retry logic with exponential backoff
- Touch-friendly mobile zoom controls

### v1.2 (Planned Q2 2027)
- Dark mode support with theme toggle
- PDF report generation
- User feedback form
- Performance optimizations (bundle size reduction)
- Frontend unit test suite expansion

### v2.0 (Planned Q3 2027)
- User authentication (OAuth 2.0, Google Workspace, Azure AD)
- Role-based access control (admin, analyst, read-only)
- Multi-month analysis (Feb-Dec 2026, year-over-year comparison)
- Regional wind farm breakdown
- Weather event correlation (annotate charts with storms, fronts)
- Forecast provider comparison (Elexon vs National Grid ESO)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, code style, and PR guidelines.

## License

[Specify license]

---

**Project Repository**: [GitHub URL]  
**Documentation**: [docs/](docs/)  
**Issues**: [GitHub Issues URL]
