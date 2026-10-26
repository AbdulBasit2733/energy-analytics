# Demo Script

## Purpose

This script guides you through a live demonstration of the UK Wind Forecast Accuracy Dashboard. Designed for presenting to stakeholders, clients, or during technical reviews.

**Duration:** 10-12 minutes  
**Audience:** Electricity procurement analysts, trading desk managers, technical evaluators  
**Presenter:** Full Stack Engineer

---

## Pre-Demo Checklist

### Technical Setup
- [ ] Backend running: `http://localhost:8000/api/health` returns `200 OK`
- [ ] Frontend running: `http://localhost:5173` loads successfully
- [ ] Browser: Chrome/Firefox with DevTools ready (F12)
- [ ] Screen resolution: 1920×1080 or higher (for best visual)
- [ ] Zoom level: 100% (avoid browser zoom)
- [ ] Close unnecessary tabs and applications
- [ ] Disable notifications (Focus Assist / Do Not Disturb)

### Demo Data Verification
```bash
# Verify cache loaded with 100% completeness
curl http://localhost:8000/api/health
# Expected: {"status": "ok", "cache_loaded": true, "total_pairs": 744}
```

### Browser Bookmarks (Pre-loaded)
1. Dashboard: `http://localhost:5173/`
2. Time Series: `http://localhost:5173/time-series`
3. Accuracy: `http://localhost:5173/accuracy`
4. API Health: `http://localhost:8000/api/health`
5. API Docs: `http://localhost:8000/docs`

---

## Script

### Part 1: Introduction (1 min)

**[Screen: Dashboard landing page]**

> "Good [morning/afternoon]. Today I'm presenting a UK Wind Forecast Accuracy Dashboard I've built to help electricity procurement analysts evaluate day-ahead wind generation forecasts.
>
> **The Problem:** UK energy traders purchase electricity in the day-ahead market based on wind forecasts. Forecast errors lead to either under-procurement (expensive balancing charges) or over-procurement (wasted costs). Understanding historical forecast accuracy helps traders adjust their strategies and risk buffers.
>
> **The Solution:** This dashboard analyzes January 2026 wind forecast accuracy using real data from Elexon BMRS — the official GB electricity market data source. It compares day-ahead forecasts against actual wind generation and provides actionable insights for procurement teams."

---

### Part 2: Dashboard Overview (2 min)

**[Screen: Dashboard home page, KPI grid visible]**

> "Let's start with the Dashboard Overview. This is what an analyst sees first — a snapshot of overall forecast performance for January 2026.
>
> **Six key metrics:**
> 1. **Average Actual Wind:** 14,637 MW — the mean actual wind generation across all 744 hours of January.
> 2. **Average Forecast Wind:** 14,815 MW — slightly higher than actual, hinting at a small over-forecast bias.
> 3. **MAE (Mean Absolute Error):** 892 MW — on average, forecasts miss by about 900 megawatts. For context, 900 MW is roughly the output of one large nuclear plant.
> 4. **RMSE:** 1,123 MW — this is higher than MAE because it penalizes large errors more heavily. The gap tells us there are some significant outlier days.
> 5. **Bias:** +178 MW — positive bias means forecasts tend to over-predict. Procurement teams were expecting more wind than actually materialized.
> 6. **Data Completeness:** 100% — all 744 expected hourly pairs are present. No missing data.
>
> **Key Takeaway:** Forecasts are reasonable (MAE ~6% of average generation), but there's a systematic over-forecasting tendency that traders should account for by adding a safety buffer to non-wind generation purchases."

**[Action: Scroll down, show loading skeleton if applicable, then scroll back up]**

> "These cards load data from the backend API. On first load, you'd see skeleton placeholders while data is fetched. Subsequent loads are instant because TanStack Query caches the response."

---

### Part 3: Time Series Visualization (2 min)

**[Screen: Navigate to Time Series page via sidebar]**

> "Now let's look at the Time Series page — this is where analysts dig into hourly patterns.
>
> **Chart Elements:**
> - **Blue dashed line:** Day-ahead forecasts, published before 09:00 UTC on D-1.
> - **Green solid line:** Actual wind generation, half-hourly data averaged to hourly.
> - **Red shaded area:** The error — where forecast and actual diverge.
>
> **What we're seeing:**
> - Notice how the lines track each other closely most of the time — that's a good forecast.
> - But look at [hover over a large error period] this period around January [X] — wide red gap. The forecast predicted much higher wind than occurred. This is when procurement teams would have been caught short on traditional generation and had to pay balancing prices.
>
> **Interactive Features:**
> [Hover over a data point]
> - Tooltip shows exact hour, forecast, actual, and error in megawatts.
>
> [Drag the brush component at the bottom]
> - This zoom control lets analysts focus on specific days. Drag the handles to select a date range... and the main chart zooms in. Perfect for investigating a problematic week."

**[Action: Zoom into Jan 10-15, then reset]**

---

### Part 4: Accuracy Analysis (2 min)

**[Screen: Navigate to Accuracy Analysis page]**

> "The Accuracy Analysis page is for analysts who want the detailed numbers.
>
> **Top section:** Overall metrics summary — same MAE, RMSE we saw on the dashboard, plus:
> - **MAPE:** 6.12% — percentage error. Caveat: this excludes hours with near-zero actual wind to avoid division-by-zero.
> - **Max Over-Forecast:** 3,246 MW — the single worst over-prediction.
> - **Correlation:** 0.9823 — near 1.0 means forecasts strongly track actual trends.
>
> **Daily Metrics Table:**
> [Scroll to table]
> This breaks down MAE, RMSE, and bias per day. Let me sort by MAE descending...
>
> [Click MAE column header]
> - January [X] had the worst accuracy — MAE over [Y] MW. An analyst would flag this day: 'What happened? Storm? Grid constraint?'
> - The best days show MAE under 500 MW — very accurate.
>
> **Error Distribution Histogram:**
> [Scroll to histogram]
> - X-axis: Error bins (negative = under-forecast, positive = over-forecast)
> - Most hours cluster near zero — good.
> - But notice the tail extending into the +1500 to +2000 MW range — those are the over-forecast outliers pulling up the RMSE."

---

### Part 5: Procurement Insights (1.5 min)

**[Screen: Navigate to Procurement Insights page]**

> "This page translates accuracy metrics into actionable intelligence for procurement teams.
>
> **Over/Under-Forecast Analysis:**
> [Point to bias indicator]
> - The positive bias (+178 MW) tells traders: 'Forecasts are slightly optimistic. Don't rely 100% on them — buy a buffer of traditional generation.'
>
> **Top Error Days:**
> [Point to table]
> - These five days had the largest errors. Procurement teams would review their day-ahead positions for these dates: 'Did we get caught out? What were the balancing costs?'
>
> **Risk Assessment:**
> [Point to RMSE interpretation]
> - RMSE of 1,123 MW falls in the 'moderate risk' category. Guidance: add a 10-15% buffer to wind-reliant positions.
>
> **Important Caveat:**
> [Point to disclaimer at bottom]
> - This is historical analysis only — not trading advice. Professional judgment required. But it gives traders a data-driven starting point."

---

### Part 6: Data Transparency (1 min)

**[Screen: Navigate to Data Transparency page]**

> "Transparency is critical for trust. This page explains exactly how the analysis works.
>
> **Accordion sections:**
> [Expand 'Forecast Cutoff Logic']
> - Cutoff: 09:00 UTC on D-1. Why? Because that's when the N2EX GB day-ahead auction closes. Only forecasts published before this time are operationally useful.
> - Selection: Latest forecast run before cutoff. Example: For January 15 delivery, we used the forecast published at 07:30 UTC on January 14.
>
> [Expand 'Resolution Mismatch']
> - Elexon's actuals are half-hourly, but forecasts are hourly. Solution: We average two consecutive half-hours. Clear documentation prevents misunderstandings.
>
> [Expand 'Data Completeness']
> - 744/744 hours present. If this were less than 100%, analysts would see a warning and could decide whether the analysis is still valid."

---

### Part 7: Technical Deep Dive — Backend API (1.5 min)

**[Screen: Open `http://localhost:8000/docs` in new tab]**

> "Behind the scenes: a FastAPI backend with automatic interactive documentation.
>
> **Key Endpoints:**
> - `/api/health` — Cache status. Let me execute this live...
>
> [Click 'Try it out' → Execute on `/api/health`]
> - Response: 200 OK, cache loaded, 744 pairs. The backend is healthy.
>
> - `/api/dashboard/kpis` — Returns all six KPI metrics.
> - `/api/timeseries` — 744 hourly forecast-actual pairs for charting.
> - `/api/accuracy/daily` — Per-day breakdown for the table we saw.
>
> **Tech Stack:**
> - FastAPI (Python 3.12) with Pydantic v2 for type-safe validation
> - HTTPX for async calls to Elexon API
> - NumPy/Pandas for metrics calculation
> - Two-tier cache: in-memory + file-based. After first startup, zero API dependency — all data served from cache."

**[Screen: Open browser DevTools Network tab, refresh dashboard]**

> "Let's see this in action. Refresh the dashboard...
>
> [Show Network tab]
> - API calls: `/api/dashboard/kpis`, `/api/metadata`, all return in under 50ms. No database queries — pure in-memory lookups."

---

### Part 8: Technical Deep Dive — Frontend (1 min)

**[Screen: Return to dashboard, open DevTools Console]**

> "Frontend: React 19 with Vite, Tailwind CSS v4, and Recharts for visualizations.
>
> **Key Decisions:**
> - **Tailwind v4:** CSS-first configuration. All theme tokens in `index.css` using oklch color space for perceptual uniformity and accessibility.
> - **shadcn/ui:** Component library for accessible, customizable UI primitives. Not an npm package — components copied into the codebase for full control.
> - **TanStack Query:** Smart data fetching with caching. Historical data has `staleTime: Infinity` — never refetches unless cache cleared.
> - **Recharts:** React-native charting library. Supports responsive, accessible charts with tooltips and legends.
>
> **Accessibility:**
> - WCAG AA contrast (4.5:1 minimum) verified on all text
> - Full keyboard navigation — try it: [Press Tab to cycle through sidebar links]
> - Screen reader support via ARIA labels
> - Responsive: works down to 375px mobile screens."

**[Action: Resize browser to mobile width, show responsive layout, resize back]**

---

### Part 9: Testing & Validation (1 min)

**[Screen: Terminal, backend directory]**

> "Quality assurance: 46 automated backend tests using pytest.
>
> **Let me run them live:**

```bash
cd backend
pytest -v
```

> [Wait for tests to pass]
> - 46 tests, all green. Coverage includes:
>   - Half-hourly to hourly aggregation
>   - Forecast selection at D-1 cutoff
>   - Rejection of post-cutoff forecasts
>   - MAE, RMSE, MAPE, Bias calculations
>   - Handling of missing data and edge cases
>
> **Integration validation:**
> - Real Elexon API test: 100% data completeness verified
> - Cross-check: January 15 forecast selection confirmed (publishTime 07:30 UTC on Jan 14, before 09:00 cutoff)
>
> **Frontend:**
> - TypeScript compilation: 0 errors
> - Production build: Clean
> - Manual testing: All pages verified on Chrome, Firefox, Safari"

---

### Part 10: Docker Deployment (1 min)

**[Screen: Terminal, project root]**

> "Deployment: Docker Compose for single-command orchestration.
>
> **Let me show you:**

```bash
docker compose up --build -d
```

> [Wait for containers to start]
> - Backend container: Python app running on port 8000
> - Frontend container: Nginx serving static build on port 3000
> - Persistent volume: Cache directory mounted, survives restarts
>
> **Access deployed app:**
> [Open `http://localhost:3000` in browser]
> - Same dashboard, now containerized. Ready for Railway, Render, AWS ECS, or any Docker host.
>
> **Production considerations:**
> - Backend needs persistent volume at `/app/cache` to preserve cached data
> - Frontend env var `VITE_API_URL` points to backend domain
> - CORS configured with frontend origin
> - Health checks on `/api/health` for load balancer routing"

**[Action: Stop containers]**

```bash
docker compose down
```

---

### Part 11: Documentation & Deliverables (0.5 min)

**[Screen: File explorer, open `docs/` folder]**

> "Complete documentation package — 15+ Markdown files:
> - **PRD, SRS, ARCHITECTURE:** Requirements and design
> - **FORECAST_METHODOLOGY:** Cutoff logic, aggregation, metrics formulas with worked examples
> - **DATA_DICTIONARY:** Every field definition from Elexon datasets
> - **API.md:** All endpoint specs with examples
> - **USER_GUIDE:** End-user manual (42 pages)
> - **TESTING, DEPLOYMENT, SECURITY:** Operational guides
> - **DECISIONS.md:** 14 architecture decision records (ADRs)
> - **GLOSSARY:** 80+ terms defined
>
> **Plus 8 Word documents** (.docx) in `deliverables/` for stakeholder review."

---

### Part 12: Conclusion & Q&A (0.5 min)

> "**Summary:**
> - **Problem:** Forecast errors cost money. Traders need data-driven insights.
> - **Solution:** This dashboard analyzes 744 hours of January 2026 data, revealing a +178 MW over-forecast bias and 892 MW average error.
> - **Value:** Procurement teams can adjust risk buffers, investigate worst days, and improve day-ahead bidding strategies.
> - **Tech:** Modern stack (React 19, FastAPI, Docker), production-ready, 46 tests, 100% data completeness.
>
> **Questions?"**

---

## Post-Demo Follow-Up

### Likely Questions & Answers

**Q: Can this be extended to other months?**  
A: Yes. The API parameters (`ANALYSIS_YEAR`, `ANALYSIS_MONTH`) are configurable. Cache manager would need to fetch additional months, and frontend would need date range selectors (planned for v1.1).

**Q: Why January 2026?**  
A: Representative winter month (high wind season). Complete dataset available (744/744 hours). No clock changes (GMT throughout). Good baseline for accuracy assessment.

**Q: What if Elexon API is down?**  
A: Two-tier cache means after first startup, the dashboard runs independently — zero API dependency. Cache survives container restarts if persistent volume mounted.

**Q: How accurate is "good enough"?**  
A: Industry benchmark: MAE 800–1,200 MW is typical for GB day-ahead wind forecasts. This dashboard's 892 MW is within expected range. RMSE <1,500 MW is generally acceptable.

**Q: Can we compare multiple forecast providers?**  
A: Not in v1.0 (only Elexon WINDFOR). Future enhancement: integrate National Grid ESO or private provider forecasts for comparison.

**Q: Is this production-ready?**  
A: Yes for internal use. For public deployment, consider adding: authentication, rate limiting, monitoring/alerting, dark mode (user feedback).

---

## Demo Tips

### Do's
- ✅ Speak to the audience (not the screen)
- ✅ Use concrete numbers ("892 MW" not "around 900")
- ✅ Pause after key points (let insights land)
- ✅ Show real interactions (hover, click, zoom)
- ✅ Admit limitations ("This doesn't cover intraday forecasts")

### Don'ts
- ❌ Rush through slides (let charts breathe)
- ❌ Apologize for features not built ("Sorry, no dark mode" → just skip it)
- ❌ Read documentation verbatim (summarize)
- ❌ Assume technical knowledge (define MAE, RMSE first)
- ❌ Skip the "why" (always explain business value)

### Backup Plan
- **If demo app crashes:** Have screenshots of each page ready
- **If API fails:** Pre-recorded video of working dashboard
- **If network down:** Static HTML export with sample data

---

## Document Version

**Version:** 1.0  
**Last Updated:** 2026-10-26  
**Duration:** 10-12 minutes  
**Presenter:** [Your Name]
