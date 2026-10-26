# Architecture and Design Decisions

## Decision Log

This document records significant technical and design decisions made during project development.

---

## ADR-001: Day-Ahead Forecast Cutoff Time

**Date:** 2026-10-25  
**Status:** Accepted  
**Context:** Need to determine which forecast run to use for comparing against actual generation.

**Decision:** Use 09:00 UTC on D-1 (day before delivery) as cutoff time.

**Rationale:**
- N2EX GB day-ahead auction closes ~09:00–09:30 UK time
- Procurement analysts must submit bids before gate closure
- Only forecasts published before cutoff are operationally useful
- January = GMT (UTC+0), so UK time = UTC

**Alternatives Considered:**
1. **12:00 UTC cutoff** — Rejected: Too late for day-ahead market participation
2. **Use all forecasts** — Rejected: Includes post-gate forecasts with no trading value
3. **Midnight cutoff** — Rejected: Too early; misses morning forecast updates

**Consequences:**
- Clear, defensible methodology aligned with market practice
- Excludes forecasts published after 09:00 UTC on D-1
- Cutoff hour configurable via `FORECAST_CUTOFF_HOUR` env var

**References:**
- Nord Pool N2EX market rules
- `docs/FORECAST_METHODOLOGY.md`

---

## ADR-002: Half-Hourly to Hourly Aggregation

**Date:** 2026-10-25  
**Status:** Accepted  
**Context:** FUELHH (actuals) is half-hourly, WINDFOR (forecasts) is hourly. Direct comparison requires matching resolution.

**Decision:** Average two consecutive FUELHH half-hours into one hourly value.

**Rationale:**
- Preserves actual energy generation more accurately than duplicating forecast
- Simple, transparent calculation: `(HH1 + HH2) / 2`
- Industry-standard approach for resolution harmonization
- Avoids artificially inflating sample size

**Alternatives Considered:**
1. **Duplicate hourly forecast for both half-hours** — Rejected: Inflates sample size, misrepresents 30-min variation
2. **Use first half-hour only** — Rejected: Discards 50% of data
3. **Interpolate to 15-min** — Rejected: Adds complexity without benefit

**Consequences:**
- 744 hourly pairs (31 days × 24 hours)
- Clear documentation required for users
- Edge case: If only 1 half-hour present, use as-is (flag as incomplete)

**References:**
- `docs/FORECAST_METHODOLOGY.md` — Aggregation section
- `backend/app/services/data_processor.py` — `aggregate_fuelhh_to_hourly()`

---

## ADR-003: Two-Tier Caching Strategy

**Date:** 2026-10-25  
**Status:** Accepted  
**Context:** Elexon API has no rate limits but is slow (~30 calls for January). Historical data never changes. Minimize API dependency.

**Decision:** Implement two-tier cache: in-memory dict + file-based JSON.

**Rationale:**
- **First startup:** Fetch from Elexon API, store in memory + write to disk
- **Subsequent startups:** Load from disk, zero API calls
- January 2026 is historical — data immutable
- Reduces startup time from 2-3 min to <5 sec

**Alternatives Considered:**
1. **No caching** — Rejected: Slow every startup, unnecessary API load
2. **Database (SQLite)** — Rejected: Overkill for read-only historical data
3. **Redis** — Rejected: Adds dependency, complexity for single-instance deployment
4. **CDN caching** — Rejected: Static files don't fit API response structure

**Consequences:**
- `/app/cache` directory must persist across container restarts
- Requires persistent volume in production (Railway, Render, ECS)
- Cache invalidation: manual (delete cache dir to force re-fetch)
- Cache files ~2-3 MB total (JSON format, uncompressed)

**References:**
- `backend/app/services/cache_manager.py`
- `docs/DEPLOYMENT.md` — Cache Strategy section

---

## ADR-004: React 19 + Vite 8 + Tailwind CSS v4

**Date:** 2026-10-25  
**Status:** Accepted  
**Context:** Frontend tech stack selection for modern, performant, accessible UI.

**Decision:**
- **React 19.3** (latest stable)
- **Vite 8.3.4** (build tool)
- **Tailwind CSS v4.3** (CSS framework, CSS-first config)
- **shadcn/ui CLI v4** (component library)
- **Recharts 3** (charting)
- **TanStack Query 5** (data fetching)

**Rationale:**
- **React 19:** Server Components, improved Suspense, concurrent rendering
- **Vite 8:** Fast HMR, native ESM, optimized production builds
- **Tailwind v4:** CSS-first config (`@import "tailwindcss"` + `@theme {}`), no JS config file
- **shadcn/ui v4:** CLI-based, customizable, accessible components (not npm package)
- **Recharts:** React-native charting, good TypeScript support, simple API
- **TanStack Query:** Robust caching, stale-while-revalidate, perfect for static data

**Alternatives Considered:**
1. **Next.js** — Rejected: Overkill for SPA without SSR needs
2. **Chart.js** — Rejected: Not React-native, requires wrapper
3. **D3.js** — Rejected: Too low-level, steep learning curve
4. **Tailwind v3** — Rejected: Outdated config format

**Consequences:**
- No `tailwind.config.ts` file (Tailwind v4 CSS-first)
- shadcn/ui components copied into `src/components/ui/` (not installed as package)
- Build output ~800 KB (acceptable with Recharts included)
- TypeScript compilation strict mode (0 errors)

**References:**
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/src/index.css` — Tailwind v4 config

---

## ADR-005: Python 3.12 + FastAPI + Pydantic v2

**Date:** 2026-10-25  
**Status:** Accepted  
**Context:** Backend API framework selection for type-safe, async, modern API.

**Decision:**
- **Python 3.12+**
- **FastAPI 0.162.0** (async web framework)
- **Pydantic v2** (data validation)
- **HTTPX** (async HTTP client)
- **Pandas + NumPy** (data processing)
- **pytest** (testing)

**Rationale:**
- **FastAPI:** Automatic OpenAPI docs, Pydantic integration, async-first, high performance
- **Pydantic v2:** Type validation, JSON schema generation, 5-50x faster than v1
- **HTTPX:** Async HTTP, retry logic, connection pooling (vs requests = sync-only)
- **Pandas:** DataFrame operations for time-series aggregation
- **NumPy:** Vectorized metrics calculation (MAE, RMSE, etc.)

**Alternatives Considered:**
1. **Flask** — Rejected: Sync-only, no automatic validation
2. **Django** — Rejected: Too heavy for API-only app, no async ORM
3. **requests** — Rejected: Sync HTTP client (HTTPX chosen for async)
4. **Polars** — Rejected: Less mature than Pandas, minimal benefit for this scale

**Consequences:**
- Async all the way: `async def` routes, `await` for I/O
- Type hints everywhere (enforced by Pydantic)
- Automatic `/docs` (Swagger UI) and `/redoc` endpoints
- 46 pytest tests covering core logic

**References:**
- `backend/requirements.txt`
- `backend/app/main.py`

---

## ADR-006: No Database

**Date:** 2026-10-25  
**Status:** Accepted  
**Context:** Need to store 744 hourly pairs + metadata. Decide between database vs in-memory.

**Decision:** No database. Store all data in-memory (Python dict) after loading from cache.

**Rationale:**
- **Data size:** 744 hourly pairs = ~100 KB in memory
- **Read-only:** No writes after cache warm
- **Performance:** Dict lookup O(1), faster than any database query
- **Simplicity:** No schema migrations, connection pooling, or query optimization
- **Deployment:** One less service to manage

**Alternatives Considered:**
1. **SQLite** — Rejected: Overkill for read-only 744 records
2. **PostgreSQL** — Rejected: Heavy dependency for small dataset
3. **Redis** — Rejected: Adds external dependency for single-instance app

**Consequences:**
- Entire dataset must fit in RAM (~512 MB sufficient)
- Horizontal scaling requires shared cache (see ADR-003 alternatives)
- No complex queries (but not needed for this use case)
- Data lost if cache files deleted + Elexon API unavailable

**References:**
- `backend/app/services/cache_manager.py`

---

## ADR-007: MAPE Excludes Near-Zero Actuals

**Date:** 2026-10-25  
**Status:** Accepted  
**Context:** MAPE (Mean Absolute Percentage Error) explodes to infinity when actual generation near zero.

**Decision:** Exclude hours where `actual_mw <= 1.0` from MAPE calculation.

**Rationale:**
- Wind generation can drop to <100 MW during calm periods
- MAPE = `|forecast - actual| / actual × 100%`
- When actual ≈ 0, MAPE → ∞ even for small absolute errors
- 1 MW threshold filters out only extreme calm periods (rare)
- MAE and RMSE remain primary metrics (not affected by zero actuals)

**Alternatives Considered:**
1. **Include all hours** — Rejected: Produces meaningless MAPE values (>1000%)
2. **Higher threshold (100 MW)** — Rejected: Excludes too much valid data
3. **Don't calculate MAPE** — Rejected: Users expect MAPE despite limitations

**Consequences:**
- MAPE reported with caveat: "Excludes hours with actual generation ≤1 MW"
- MAPE can be `null` if all actuals ≤1 MW (rare for January wind)
- Documentation emphasizes MAE and RMSE as primary metrics

**References:**
- `backend/app/services/accuracy_metrics.py`
- `docs/FORECAST_METHODOLOGY.md` — MAPE section

---

## ADR-008: Single Theme (Light Mode Only)

**Date:** 2026-10-26  
**Status:** Accepted  
**Context:** Dark mode support adds development + testing time. 16-hour project budget.

**Decision:** Light mode only for initial release.

**Rationale:**
- **User context:** Procurement analysts work in office environments with good lighting
- **Time budget:** Dark mode doubles theme testing surface
- **Chart legibility:** Light backgrounds better for data visualization (industry standard)
- **Accessibility:** Easier to meet WCAG AA contrast in light mode

**Alternatives Considered:**
1. **Dark mode first** — Rejected: Light mode more common for analytics dashboards
2. **Both themes** — Rejected: Out of scope for 16-hour budget
3. **Auto-detect** — Rejected: Requires both themes implemented

**Consequences:**
- No `prefers-color-scheme` detection
- Single color palette to test and maintain
- Future enhancement: Dark mode can be added post-MVP
- Users cannot toggle theme

**References:**
- `docs/UI_UX_DESIGN_SYSTEM.md` — Dark Mode section

---

## ADR-009: Forecast History API Includes All Runs

**Date:** 2026-10-26  
**Status:** Accepted  
**Context:** WINDFOR API returns multiple forecast runs per day (~6-10 runs). Need to decide which to return in `/api/forecast-history` endpoint.

**Decision:** Return all forecast runs for requested delivery date, mark selected run.

**Rationale:**
- **Transparency:** Users can see all available forecasts, not just selected one
- **Analysis:** Supports "how did forecast accuracy evolve through the day" questions
- **Validation:** Users can verify cutoff logic by comparing publish times
- **Data size:** ~10 runs × 24 hours = 240 records per day (acceptable)

**Alternatives Considered:**
1. **Return only selected run** — Rejected: Reduces transparency, hides forecast evolution
2. **Separate endpoint for all runs** — Rejected: Adds complexity, splits related data

**Consequences:**
- Response size larger (~10 KB vs ~1 KB for single run)
- Frontend must filter/highlight selected run
- `is_selected: true` flag indicates cutoff-selected forecast

**References:**
- `backend/app/routers/forecast_history.py`
- `docs/API.md` — `/api/forecast-history` section

---

## ADR-010: No Real-Time Data Pipeline

**Date:** 2026-10-26  
**Status:** Accepted  
**Context:** Elexon API provides real-time data. Decide between static historical vs live streaming.

**Decision:** Static historical data only (January 2026).

**Rationale:**
- **Scope:** Take-home assignment focuses on analysis, not real-time infrastructure
- **Complexity:** Real-time requires websockets, polling, data freshness monitoring
- **Value:** Forecast accuracy analysis is retrospective (historical data sufficient)
- **Time budget:** 16 hours insufficient for robust real-time pipeline

**Alternatives Considered:**
1. **Real-time updates** — Rejected: Out of scope, high complexity
2. **Daily batch updates** — Rejected: Requires scheduling, monitoring
3. **User-triggered refresh** — Rejected: Increases backend load, cache invalidation complexity

**Consequences:**
- Dashboard displays fixed January 2026 data
- No automatic updates or live data feeds
- Future enhancement: Add date range selector + batch update mechanism
- Users cannot analyze current month

**References:**
- `docs/PRD.md` — Non-Functional Requirements

---

## ADR-011: Client-Side Routing (React Router)

**Date:** 2026-10-26  
**Status:** Accepted  
**Context:** Multi-page dashboard requires navigation solution.

**Decision:** Use React Router 7 for client-side routing.

**Rationale:**
- **SPA benefits:** No full page reload, instant navigation
- **Browser history:** Back/forward buttons work correctly
- **Deep linking:** Direct URLs to specific pages (e.g., `/accuracy`)
- **Industry standard:** React Router is de-facto standard for React SPAs

**Alternatives Considered:**
1. **Single-page (no routing)** — Rejected: Poor UX for multi-section dashboard
2. **Hash routing** — Rejected: Ugly URLs (#/accuracy), poor SEO
3. **Multi-page app** — Rejected: Full reloads, state loss

**Consequences:**
- Nginx/server must redirect all routes to `index.html` (SPA fallback)
- `nginx.conf` includes `try_files $uri $uri/ /index.html;`
- Routes: `/`, `/time-series`, `/accuracy`, `/procurement`, `/transparency`

**References:**
- `frontend/src/App.tsx`
- `frontend/nginx.conf`

---

## ADR-012: Test Strategy (pytest + integration, minimal frontend tests)

**Date:** 2026-10-26  
**Status:** Accepted  
**Context:** 16-hour budget requires prioritized testing. Decide coverage vs effort trade-off.

**Decision:**
- **Backend:** Comprehensive pytest unit tests (46 tests)
- **Integration:** Real Elexon API validation
- **Frontend:** Build validation + manual testing (Vitest setup in place, tests not fully implemented)

**Rationale:**
- **Backend complexity:** Core business logic (aggregation, selection, metrics) = high-value testing
- **Frontend determinism:** React components harder to test meaningfully vs visual inspection
- **Risk:** Data processing errors more costly than UI layout issues
- **Time:** Backend tests = 2-3 hr, full frontend tests = 4-5 hr (excessive)

**Alternatives Considered:**
1. **Full frontend test suite** — Rejected: Low ROI for time invested
2. **No backend tests** — Rejected: Unacceptable risk for data accuracy
3. **E2E tests only** — Rejected: Slow, brittle, harder to debug

**Consequences:**
- 46 pytest tests covering all backend services
- Frontend TypeScript compilation validated (0 errors)
- Manual UI testing via browser (all pages verified)
- Vitest configured for future frontend test expansion

**References:**
- `docs/TESTING.md`
- `backend/tests/`

---

## ADR-013: UI/UX Pro Max Skill for Design System

**Date:** 2026-10-26  
**Status:** Accepted  
**Context:** Project requirements mandate UI/UX Pro Max skill installation before frontend implementation.

**Decision:** Use UI/UX Pro Max skill for design system recommendations, document findings.

**Rationale:**
- **Requirement:** Specified in master prompt as mandatory
- **Value:** Provides structured design guidance (color, typography, motion, accessibility)
- **Documentation:** Outputs design system markdown for reference
- **Validation:** Pre-delivery checklist ensures consistency

**Alternatives Considered:**
- N/A (mandated by requirements)

**Consequences:**
- Design system documented in `docs/UI_UX_DESIGN_SYSTEM.md`
- Color palette uses oklch for perceptual uniformity
- Accessibility checklist followed (WCAG AA contrast, keyboard nav, screen reader support)
- Motion kept minimal (skeleton loaders only, no decorative animations)

**References:**
- `docs/UI_UX_DESIGN_SYSTEM.md`
- `.claude/skills/ui-ux-pro-max/` (skill files)

---

## ADR-014: Word Document Generation via python-docx

**Date:** 2026-10-26  
**Status:** Accepted  
**Context:** Requirement for 8 Word documents (.docx). Need conversion from Markdown.

**Decision:** Generate .docx files programmatically using `python-docx` library.

**Rationale:**
- **Automation:** Script converts Markdown → DOCX without manual editing
- **Consistency:** Same content in .md and .docx formats
- **Maintainability:** Single source of truth (Markdown), script regenerates .docx
- **python-docx:** Mature library, good API for headings, paragraphs, tables

**Alternatives Considered:**
1. **Pandoc** — Rejected: External dependency, harder to customize output
2. **Manual Word editing** — Rejected: Error-prone, not maintainable
3. **LibreOffice headless** — Rejected: Heavy dependency, complex setup

**Consequences:**
- `deliverables/generate_docx.py` script converts 8 Markdown files to DOCX
- Formatting: Headings styled, code blocks as monospace, tables preserved
- Run script: `python deliverables/generate_docx.py`
- Output: `deliverables/*.docx` (8 files)

**References:**
- `deliverables/generate_docx.py`
- `backend/requirements.txt` — includes `python-docx`

---

## Future Decision Points

### Open Questions
1. **Multi-month analysis:** Extend to other months (Feb-Dec 2026)?
2. **Real-time pipeline:** Add live data ingestion?
3. **Forecast provider comparison:** Compare Elexon vs other providers?
4. **User authentication:** Add login for personalized views?
5. **Export functionality:** CSV, PDF, PNG chart export?

### Deferred Decisions
- **Dark mode:** Deferred to post-MVP (ADR-008)
- **Date range filters:** Deferred to v1.1 (currently shows full January only)
- **Advanced visualizations:** Heatmaps, box plots, etc. (Recharts basic charts sufficient for MVP)

---

## References

- `docs/PRD.md` — Product requirements
- `docs/SRS.md` — Software requirements specification
- `docs/ARCHITECTURE.md` — System architecture
- `docs/FORECAST_METHODOLOGY.md` — Forecast selection logic
- `README.md` — Project overview
