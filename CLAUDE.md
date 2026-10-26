# UK Wind Forecast Accuracy Dashboard

## Project
Full-stack analytics dashboard for UK electricity procurement analysts. Compares Elexon BMRS wind generation forecasts against actuals for January 2026.

## Stack
- Backend: Python 3.12+ / FastAPI / Pydantic v2 / HTTPX / Pandas / NumPy
- Frontend: React 19 / TypeScript / Vite / Tailwind CSS v4 / shadcn/ui / Recharts / TanStack Query
- Infrastructure: Docker / Docker Compose

## Key Decisions
- FUELHH API uses `settlementDateFrom`/`settlementDateTo` (YYYY-MM-DD), NOT `from`/`to`
- WINDFOR is hourly; FUELHH is half-hourly. Actuals are averaged to hourly for comparison.
- Forecast cutoff: 09:00 UTC on D-1 (configurable via FORECAST_CUTOFF_HOUR env var)
- January 2026 is GMT (UTC+0) — no BST considerations
- All timestamps stored and compared in UTC
- Bias sign convention: positive = forecast exceeded actual (over-forecast)

## Commands
- Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev`
- Backend tests: `cd backend && pytest -v`
- Frontend tests: `cd frontend && npm test`
- Docker: `docker compose up --build`

## Structure
- `backend/` — FastAPI application
- `frontend/` — React SPA
- `docs/` — Markdown documentation
- `deliverables/` — Word documents (.docx)
