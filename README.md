# UK Wind Forecast Accuracy Dashboard

A full-stack web application for UK electricity procurement analysts to analyse the accuracy of national wind generation forecasts against actual generation data for January 2026.

## Problem

UK electricity procurement analysts need to make day-ahead purchasing decisions based on wind generation forecasts. These forecasts are published by the Balancing Mechanism Reporting Service (BMRS) operated by Elexon. Understanding forecast accuracy — and specifically which forecast was available at the time of the purchasing decision — is critical for managing procurement costs.

This dashboard answers two key questions:
1. **What wind forecast was available** when the day-ahead purchasing decision needed to be made?
2. **How accurate were those forecasts** compared with actual wind generation?

## Features

- **Dashboard Overview** — KPI cards showing MAE, RMSE, Bias, MAPE, data completeness, and average generation
- **Forecast vs Actual Chart** — Hourly time-series comparison with zoom/pan across 744 data points
- **Forecast Publication History** — View all forecast runs for a delivery date, showing which was selected at cutoff
- **Accuracy Analysis** — Error distribution histogram, daily metrics table, MAE/bias over time charts
- **Procurement Insight** — Bias direction analysis, uncertainty assessment, worst-error day identification
- **Data & Methodology** — Full transparency on data sources, aggregation, cutoff logic, and metric formulas

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19.3, TypeScript, Vite 8.3, Tailwind CSS v4.3, Recharts 3, TanStack Query |
| Backend | Python 3.12, FastAPI, Pydantic v2, HTTPX, Pandas, NumPy |
| Testing | pytest (46 tests), Vitest |
| Infrastructure | Docker, Docker Compose, Nginx |
| Data Source | Elexon BMRS API (FUELHH + WINDFOR datasets) |

## Prerequisites

- Docker and Docker Compose (for containerised startup)
- OR: Node.js 22+, Python 3.12+, npm (for local development)

## Quick Start (Docker)

```bash
git clone https://github.com/AbdulBasit2733/energy-analytics.git
cd energy-analytics
cp .env.example .env
docker compose up --build
```

The dashboard will be available at `http://localhost:3000`. The backend API is at `http://localhost:8000/api`.

On first startup, the backend fetches January 2026 data from the Elexon API and caches it to disk. Subsequent startups load from cache with zero API calls.

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp .env.example .env` to create the environment file.

If the backend image build fails while downloading packages from PyPI, check that Docker can access `pypi.org` and retry `docker compose up --build`. The backend install step retries longer network timeouts automatically.

## Quick Start (Local Development)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The frontend dev server at `http://localhost:5173` proxies `/api` requests to the backend.
For a separate frontend/backend deployment, set `VITE_API_URL` to the backend origin only (for example, `https://your-backend.example.com`, without `/api`) when building the frontend. The frontend adds `/api` to that origin. Set the backend's `CORS_ORIGINS` to include the deployed frontend origin.

## Testing

```bash
# Backend (46 tests)
cd backend && pytest -v

# Frontend build check
cd frontend && npm run build
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ELEXON_BASE_URL` | `https://data.elexon.co.uk/bmrs/api/v1` | Elexon BMRS API base URL |
| `FORECAST_CUTOFF_HOUR` | `9` | UTC hour on D-1 for forecast selection cutoff |
| `ANALYSIS_YEAR` | `2026` | Year for analysis |
| `ANALYSIS_MONTH` | `1` | Month for analysis (January) |
| `CACHE_DIR` | `./cache` | Directory for cached API responses |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Allowed CORS origins |
| `VITE_API_URL` | `/api` (relative) | Backend origin for the frontend; use the origin only, without an `/api` suffix |

## API Documentation

The FastAPI backend provides automatic OpenAPI documentation at `http://localhost:8000/docs`.

Key endpoints:
- `GET /api/health` — Cache status and data availability
- `GET /api/dashboard/kpis` — Aggregated KPI metrics
- `GET /api/timeseries?date=2026-01-15` — Hourly forecast vs actual
- `GET /api/forecast-history?date=2026-01-15` — All forecast runs for a delivery date
- `GET /api/accuracy/summary` — Overall accuracy metrics
- `GET /api/accuracy/daily` — Per-day accuracy breakdown
- `GET /api/metadata` — Data source and methodology details

## Repository Structure

```
├── backend/           Python FastAPI application
│   ├── app/
│   │   ├── models/    Pydantic data models
│   │   ├── services/  Business logic (Elexon client, data processing, metrics)
│   │   ├── routers/   API endpoints
│   │   └── utils/     Time helpers
│   └── tests/         pytest test suite (46 tests)
├── frontend/          React SPA
│   ├── src/
│   │   ├── components/  UI components (layout, dashboard, charts, accuracy)
│   │   ├── hooks/       TanStack Query data hooks
│   │   ├── lib/         API client, utilities, constants
│   │   └── pages/       Route-level page components
│   └── tests/         Vitest test setup
├── docs/              Markdown documentation (19 files)
├── deliverables/      Word documents (.docx, 8 files)
└── docker-compose.yml Docker Compose configuration
```

## Key Technical Decisions

1. **Resolution mismatch**: FUELHH (actuals) is half-hourly; WINDFOR (forecasts) is hourly. Two half-hours are averaged to one hourly value for comparison.
2. **Forecast cutoff**: 09:00 UTC on D-1, matching the N2EX GB day-ahead auction close time. Configurable via environment variable.
3. **Caching**: Two-tier (in-memory + file). January 2026 data is historical and cached aggressively — after first fetch, the backend requires zero API calls.
4. **API parameters**: FUELHH uses `settlementDateFrom`/`settlementDateTo` (not `from`/`to`). Discovered through live API testing.

## Data Source

All data comes from the [Elexon BMRS API](https://bmrs.elexon.co.uk/api-documentation), the official source for GB electricity market data. No API key is required.

- **FUELHH** — Actual half-hourly generation by fuel type (filtered to WIND)
- **WINDFOR** — Wind generation forecast with publication timestamps

## AI Tools Used

- **Claude Opus 4.6** (Anthropic) — Primary development assistant for all code, documentation, and architecture decisions.

## Known Limitations

- Analysis restricted to January 2026 delivery periods
- MAPE excluded for hours where actual generation ≤ 1 MW (division by near-zero)
- Forecast history depends on Elexon API returning historical publication timestamps
- No consumer demand data — procurement insights are indicative only
- Single-month scope — seasonal patterns cannot be assessed
