# Assumptions and Limitations

## Purpose

This document explicitly states assumptions made during development and known limitations of the dashboard. Understanding these constraints is critical for interpreting results and making informed decisions based on the analysis.

---

## Data Assumptions

### A1: Elexon BMRS Data Accuracy

**Assumption:** Elexon BMRS API provides accurate, complete, and authoritative data for UK wind generation.

**Justification:**
- Elexon is the official Balancing and Settlement Code Company for GB electricity market
- FUELHH and WINDFOR datasets are industry-standard references
- Data used for settlement and billing across the GB market

**Risk:** If Elexon data contains errors, dashboard analysis inherits those errors.

**Mitigation:** Cross-reference with National Grid ESO data where discrepancies suspected.

---

### A2: Data Completeness for January 2026

**Assumption:** All 744 expected hourly pairs (31 days × 24 hours) are present in the Elexon API.

**Actual Result:** 100% completeness (744/744 pairs) verified during integration testing.

**Risk:** Future months may have missing data due to API outages or data quality issues.

**Mitigation:** Dashboard reports data completeness percentage; users can assess impact of missing data.

---

### A3: Forecast Publication Timing

**Assumption:** WINDFOR forecasts are published sufficiently before the 09:00 UTC cutoff on D-1 for most days.

**Verification:** Real data shows 6-10 forecast runs per day, with at least one published before 09:00 UTC cutoff for all 31 days in January 2026.

**Risk:** On rare occasions, no forecast may be published before cutoff (e.g., system outage).

**Mitigation:** Fallback logic uses earliest available forecast when no pre-cutoff forecast exists, flagged in metadata.

---

### A4: No Forecast Revisions After Cutoff

**Assumption:** Only forecasts published before 09:00 UTC on D-1 are operationally relevant for day-ahead purchasing.

**Justification:** N2EX GB day-ahead auction gate closes ~09:00–09:30 UTC on D-1. Post-cutoff forecasts have no trading value for day-ahead procurement.

**Risk:** Some market participants may use later forecasts for intraday or balancing actions.

**Mitigation:** Clearly document cutoff logic in methodology section; allow cutoff hour to be configurable via environment variable.

---

## Temporal Assumptions

### A5: January 2026 is GMT (UTC+0)

**Assumption:** No British Summer Time (BST) offset applies in January.

**Verification:** BST runs from last Sunday in March to last Sunday in October. January is always GMT.

**Risk:** None for January. Future months (Apr-Oct) require BST handling.

**Mitigation:** All timestamps stored in UTC; document timezone handling for future enhancements.

---

### A6: 48 Settlement Periods Per Day

**Assumption:** Every day in January 2026 has exactly 48 half-hour settlement periods.

**Justification:** No clock changes in January (GMT throughout). Clock-change days (last Sunday in March/October) have 46 or 50 periods.

**Verification:** Confirmed via FUELHH data inspection.

**Risk:** None for January.

**Mitigation:** Code handles variable period counts (for future multi-month support).

---

## Methodological Assumptions

### A7: Half-Hourly Averaging Preserves Accuracy

**Assumption:** Averaging two consecutive FUELHH half-hours into one hourly value accurately represents hourly generation.

**Justification:**
- Standard practice in energy analysis
- Wind generation changes gradually over 30-min periods (not abrupt)
- Error introduced by averaging << forecast error magnitude

**Limitation:** Misses sub-hourly ramp events (e.g., sudden wind drops within an hour).

**Impact:** Negligible for day-ahead accuracy analysis (sub-hourly ramps not predictable at D-1 horizon).

---

### A8: Latest Pre-Cutoff Forecast is Most Accurate

**Assumption:** The most recent forecast published before the 09:00 UTC cutoff is the best available forecast for procurement decisions.

**Justification:**
- Newer forecasts incorporate latest weather data
- Industry practice: use most recent forecast available at decision time

**Limitation:** Assumes forecast skill improves with recency (generally true but not guaranteed for every run).

**Impact:** Alternative selection criteria (e.g., ensemble average) could improve accuracy but add complexity.

---

### A9: MAPE Exclusion Threshold (1 MW)

**Assumption:** Hours with actual generation ≤1 MW are excluded from MAPE calculation to avoid division by near-zero.

**Justification:**
- MAPE = `|forecast - actual| / actual × 100%` → ∞ as actual → 0
- 1 MW threshold filters only extreme calm periods (rare)
- MAE and RMSE remain primary metrics

**Limitation:** MAPE not representative during low-wind periods (but these are rare in January).

**Impact:** MAPE slightly overestimates accuracy by excluding worst-case hours.

---

## Scope Limitations

### L1: Single Month Analysis (January 2026)

**Limitation:** Dashboard analyzes only January 2026. Results not generalizable to other months or seasons.

**Reasons:**
- 16-hour project time budget
- January selected as representative winter month (high wind season)
- Historical data availability

**Impact:**
- Cannot assess seasonal forecast accuracy trends
- Cannot compare winter vs summer performance
- January bias: higher average wind generation than summer months

**Future Enhancement:** Extend to multi-month analysis with date range selectors.

---

### L2: Day-Ahead Horizon Only

**Limitation:** Analysis covers day-ahead forecasts only (D-1 at 09:00 UTC cutoff). Does not assess intraday, week-ahead, or longer-term forecasts.

**Reasons:**
- Day-ahead accuracy most relevant for procurement teams
- Intraday forecasts have different selection logic (multiple cutoffs per day)

**Impact:** Cannot assess forecast accuracy at other horizons (2-day ahead, week-ahead, etc.).

**Future Enhancement:** Add multi-horizon analysis with separate cutoff logic per horizon.

---

### L3: Aggregated GB-Wide Wind Generation

**Limitation:** FUELHH and WINDFOR report aggregated GB-wide wind generation. No regional or wind farm–level granularity.

**Reasons:**
- Elexon datasets provide national totals only
- Wind farm–level data requires different API (e.g., National Grid ESO API)

**Impact:**
- Cannot assess regional forecast accuracy (e.g., Scotland vs England)
- Cannot identify which wind farms contribute most to forecast errors

**Future Enhancement:** Integrate National Grid ESO wind farm–level data.

---

### L4: No External Factors Considered

**Limitation:** Analysis does not account for external factors affecting forecast accuracy:
- Weather events (storms, anticyclones)
- Grid constraints (curtailment, transmission limits)
- Wind farm availability (maintenance, faults)
- Forecaster/model version changes

**Reasons:**
- Out of scope for 16-hour time budget
- Requires additional data sources (weather obs, grid constraints)

**Impact:** Cannot explain why specific days have large errors or identify root causes.

**Future Enhancement:** Integrate weather event data, grid constraint logs.

---

### L5: Static Historical Data (No Real-Time Updates)

**Limitation:** Dashboard displays pre-computed analysis for January 2026. No automatic updates or real-time data feeds.

**Reasons:**
- Take-home assignment scope (demonstrate analysis capability, not production infrastructure)
- Real-time pipeline requires websockets, polling, monitoring (4-6 hour effort)

**Impact:** Cannot analyze current or future months without manual data refresh.

**Future Enhancement:** Add scheduled batch updates, user-triggered refresh, or real-time streaming.

---

### L6: Single Forecast Provider (Elexon)

**Limitation:** Analysis uses only Elexon WINDFOR forecasts. Does not compare multiple forecast providers.

**Reasons:**
- Elexon is authoritative GB market data source
- Other providers (private weather services) not publicly accessible

**Impact:** Cannot determine if Elexon forecasts are best-in-class or identify alternative providers with better accuracy.

**Future Enhancement:** Integrate forecasts from National Grid ESO, private providers (if available).

---

## Technical Limitations

### T1: In-Memory Data Storage

**Limitation:** All data stored in Python dict (in-memory). No database.

**Reasons:**
- Small dataset (744 pairs = ~100 KB)
- Read-only access pattern
- Simplifies deployment

**Impact:**
- Horizontal scaling requires shared cache (Redis, file-based on shared volume)
- Cannot handle multi-year datasets (would exceed memory)
- Data lost if cache files deleted and Elexon API unavailable

**Future Enhancement:** Migrate to PostgreSQL or Redis for multi-instance support.

---

### T2: No User Authentication

**Limitation:** Dashboard is publicly accessible (no login required).

**Reasons:**
- Historical data only (no sensitive information)
- Take-home assignment scope

**Impact:**
- Cannot personalize views per user
- No role-based access control
- No usage tracking per user

**Future Enhancement:** Add authentication for personalized dashboards, saved filters.

---

### T3: Limited Export Functionality

**Limitation:** No built-in CSV export, PDF report generation, or chart image download.

**Reasons:**
- Time budget constraints
- Workarounds available (browser print, screenshot, copy-paste)

**Impact:** Users must manually export data for external analysis.

**Future Enhancement:** Add export buttons (CSV, PDF, PNG).

---

### T4: Single Theme (Light Mode Only)

**Limitation:** No dark mode support.

**Reasons:**
- Time budget (dark mode doubles testing surface)
- Office environment assumption (good lighting)

**Impact:** Users cannot toggle theme preference.

**Future Enhancement:** Add dark mode with `prefers-color-scheme` detection.

---

### T5: No Date Range Filters

**Limitation:** Dashboard shows full January 2026 (all 744 hours). Cannot filter by date range or specific days.

**Reasons:**
- Single-month scope makes filtering less critical
- Time budget constraints

**Impact:** Users cannot zoom into specific weeks or exclude outlier days.

**Future Enhancement:** Add date range picker, day-of-week filters.

---

## Statistical Limitations

### S1: Correlation Does Not Imply Causation

**Limitation:** High correlation (Pearson r) between forecast and actual does not prove forecast skill.

**Reason:** Correlation measures linear relationship strength, not predictive accuracy. A forecast that always predicts 10,000 MW could have high correlation if actuals center around that value.

**Impact:** Users must interpret correlation alongside MAE, RMSE, and bias.

**Mitigation:** Dashboard presents multiple metrics (MAE, RMSE, bias, MAPE, correlation) for comprehensive accuracy assessment.

---

### S2: MAPE Asymmetry

**Limitation:** MAPE treats over-forecasts and under-forecasts asymmetrically.

**Example:**
- Actual: 1,000 MW, Forecast: 1,200 MW → MAPE = 20%
- Actual: 1,200 MW, Forecast: 1,000 MW → MAPE = 16.7%

**Impact:** MAPE cannot distinguish symmetric error distributions from asymmetric ones.

**Mitigation:** Use MAE and bias as primary metrics; MAPE as supplementary.

---

### S3: No Confidence Intervals

**Limitation:** Metrics (MAE, RMSE, etc.) reported as point estimates without confidence intervals or error bars.

**Reasons:**
- Population data (all 744 hours), not sample
- Confidence intervals require assumptions (normality, independence) not verified

**Impact:** Cannot quantify uncertainty in reported metrics.

**Future Enhancement:** Bootstrap confidence intervals for metrics.

---

### S4: Temporal Autocorrelation Not Assessed

**Limitation:** Analysis treats hourly pairs as independent. Does not assess temporal autocorrelation in errors.

**Impact:**
- Consecutive hours may have correlated errors (e.g., persistent over-forecast during a multi-day weather event)
- Standard statistical tests (t-tests, ANOVA) assume independence

**Future Enhancement:** Time-series analysis (ACF, PACF) to detect error persistence.

---

## Operational Limitations

### O1: No Alerting or Monitoring

**Limitation:** Dashboard does not alert users when forecast accuracy degrades or data quality issues arise.

**Reasons:**
- Static historical data (no new data arriving)
- No user notification infrastructure

**Impact:** Users must manually check dashboard for updates.

**Future Enhancement:** Email/Slack alerts for large forecast errors, data completeness drops.

---

### O2: No User Feedback Mechanism

**Limitation:** No in-app feedback form or issue reporting.

**Reasons:**
- Take-home assignment scope

**Impact:** Users cannot report bugs or request features directly from dashboard.

**Future Enhancement:** Add feedback form, link to GitHub Issues.

---

### O3: No Performance Monitoring

**Limitation:** No instrumentation for tracking dashboard performance (load times, API response times, error rates).

**Reasons:**
- Development environment only
- Production monitoring tools (New Relic, Datadog) require paid subscriptions

**Impact:** Cannot diagnose performance regressions or user experience issues at scale.

**Future Enhancement:** Integrate APM (Application Performance Monitoring) tool.

---

## Interpretation Caveats

### C1: Historical Accuracy ≠ Future Accuracy

**Caveat:** January 2026 forecast accuracy does not guarantee similar accuracy in future months or years.

**Reasons:**
- Forecast models evolve (upgrades, retraining)
- Weather patterns change (climate variability)
- Wind farm capacity changes (new installations, decommissioning)

**Implication:** Use dashboard for retrospective analysis only; do not extrapolate to future performance.

---

### C2: Forecast Accuracy Varies by Weather Regime

**Caveat:** Accuracy metrics aggregate across all weather conditions. Performance varies by regime (e.g., better accuracy during stable anticyclones vs Atlantic storms).

**Implication:** Overall MAE/RMSE may mask poor performance in specific weather patterns.

**Future Enhancement:** Stratify accuracy by weather regime (high pressure, low pressure, frontal systems).

---

### C3: No Trading Recommendations

**Caveat:** Dashboard provides analytical insights only. **Not financial or trading advice.**

**Reasons:**
- Historical data only (not predictive)
- No consideration of market prices, risk appetite, or portfolio constraints
- Authors not licensed financial advisors

**Implication:** Users must consult qualified trading professionals before making procurement decisions based on this analysis.

---

### C4: Bias May Not Persist

**Caveat:** Observed bias (positive or negative) in January 2026 may not persist in future periods.

**Reasons:**
- Bias can result from transient model calibration issues (fixed in later versions)
- Weather patterns in January may differ from other months

**Implication:** Do not assume consistent over/under-forecasting in future periods without ongoing monitoring.

---

## Known Issues

### I1: Recharts Bundle Size

**Issue:** Recharts library adds ~400 KB to frontend bundle size.

**Impact:** Initial page load slightly slower (but still <2.5s LCP).

**Mitigation:** Recharts lazy-loaded via dynamic import; not blocking initial render.

**Resolution:** Acceptable for MVP. Future: Evaluate lightweight alternatives (e.g., visx, Chart.js with tree-shaking).

---

### I2: TypeScript `baseUrl` Deprecation Warning

**Issue:** TypeScript 5.x deprecates `baseUrl` without `paths`. Warning appears during compilation.

**Impact:** No runtime effect; cosmetic warning only.

**Mitigation:** Added `"ignoreDeprecations": "6.0"` to `tsconfig.app.json`.

**Resolution:** Warning suppressed. Full fix requires path aliases refactor (deferred).

---

### I3: No Mobile Chart Interactions

**Issue:** Recharts brush component (zoom bar) difficult to use on mobile touchscreens.

**Impact:** Mobile users cannot zoom into specific date ranges easily.

**Mitigation:** Brush component hidden on screens <768px (md breakpoint).

**Resolution:** Acceptable for MVP. Future: Implement touch-friendly zoom controls.

---

## Future Work

### Planned Enhancements
1. **Multi-month analysis** — Extend to Feb-Dec 2026, year-over-year comparison
2. **Date range filters** — User-selectable date ranges, day-of-week filters
3. **Export functionality** — CSV, PDF, PNG chart export
4. **Weather event correlation** — Annotate charts with storm events, fronts
5. **Regional breakdown** — Scotland, England, offshore wind farm analysis
6. **Forecast provider comparison** — Elexon vs National Grid ESO vs private providers
7. **Confidence intervals** — Bootstrap CIs for accuracy metrics
8. **Alerting** — Email/Slack notifications for accuracy degradation
9. **Dark mode** — Theme toggle with `prefers-color-scheme` support
10. **User authentication** — Personalized views, saved filters

---

## Summary

### Critical Assumptions to Remember
1. January 2026 only (not generalizable to other months)
2. Day-ahead horizon only (09:00 UTC D-1 cutoff)
3. GB-wide aggregated data (no regional detail)
4. No external factors (weather events, grid constraints)
5. Static historical data (no real-time updates)

### Critical Limitations to Remember
1. MAPE excludes near-zero actuals (≤1 MW)
2. No confidence intervals on metrics
3. No user authentication or personalization
4. No export functionality built-in
5. Light mode only (no dark mode)

### Key Caveats for Users
1. **Historical accuracy ≠ future accuracy**
2. **Not trading advice** — consult professionals
3. **Bias may not persist** — monitor ongoing performance
4. **Accuracy varies by weather regime** — overall metrics may mask regime-specific issues

---

## Document Version

**Version:** 1.0  
**Last Updated:** 2026-10-26  
**Author:** Development Team  
**Reviewers:** N/A (take-home assignment)

