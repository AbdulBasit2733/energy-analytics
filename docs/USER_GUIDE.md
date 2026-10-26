# User Guide

## Introduction

The **UK Wind Forecast Accuracy Dashboard** helps electricity procurement analysts evaluate the accuracy of day-ahead wind generation forecasts for January 2026. This tool compares Elexon BMRS forecasts (WINDFOR dataset) against actual wind generation (FUELHH dataset) to support better purchasing decisions in the GB day-ahead market.

### Who is this for?
- Electricity procurement analysts
- Trading desk staff
- Energy market researchers
- Grid operations teams

### What can you do?
- View overall forecast accuracy metrics (MAE, RMSE, bias)
- Compare hourly forecast vs actual wind generation
- Identify days with largest forecast errors
- Understand forecast methodology and data sources
- Export data for further analysis

---

## Getting Started

### Accessing the Dashboard

**Development:** http://localhost:5173  
**Production:** [Your deployed URL]

No login required. The dashboard is read-only and displays pre-analyzed January 2026 data.

### System Requirements

**Supported Browsers:**
- Chrome 120+
- Firefox 121+
- Safari 17+
- Edge 120+

**Minimum Screen Resolution:** 375px width (mobile) to 1920px+ (desktop)

**Internet Connection:** Required for initial load; data cached in browser after first visit.

---

## Dashboard Overview

### Navigation

The sidebar (desktop) or hamburger menu (mobile) provides access to five main pages:

1. **Dashboard** — Overview with key metrics
2. **Time Series** — Hourly forecast vs actual comparison
3. **Accuracy Analysis** — Detailed accuracy breakdown
4. **Procurement Insights** — Actionable intelligence for buyers
5. **Data Transparency** — Methodology and data sources

---

## Page-by-Page Guide

### 1. Dashboard (Home)

**Purpose:** Quick snapshot of overall forecast performance for January 2026.

#### KPI Cards (2×3 Grid)

| Metric | What it means | Typical range |
|--------|---------------|---------------|
| **Average Actual Wind** | Mean actual wind generation across all 744 hours | 10,000–16,000 MW |
| **Average Forecast Wind** | Mean forecast wind generation across all 744 hours | 10,000–16,000 MW |
| **MAE (Mean Absolute Error)** | Average magnitude of forecast errors, ignoring direction | 500–1,500 MW |
| **RMSE (Root Mean Square Error)** | Average error with larger penalties for big misses | 700–2,000 MW |
| **Bias (Mean Error)** | Systematic over/under-forecasting tendency | -500 to +500 MW |
| **Data Completeness** | % of expected hourly pairs present | Target: 100% |

**Interpretation Tips:**
- **Positive Bias:** Forecasts tend to over-predict (expect more wind than materializes)
- **Negative Bias:** Forecasts tend to under-predict (actual wind exceeds forecast)
- **RMSE > MAE:** Indicates presence of large outlier errors
- **MAE < 10% of avg actual:** Generally considered acceptable accuracy

#### Loading States
- **Skeleton cards:** Data is being fetched (first visit only, ~2-3 seconds)
- **After first load:** Data cached in browser; subsequent visits instant

---

### 2. Time Series Page

**Purpose:** Visualize hourly forecast vs actual wind generation over time.

#### Main Chart

**Chart Elements:**
- **Blue dashed line:** Forecast wind generation (WINDFOR, published D-1 before 09:00 UTC)
- **Green solid line:** Actual wind generation (FUELHH, half-hourly averaged to hourly)
- **Red shaded area:** Forecast error (difference between forecast and actual)

**Interactions:**
- **Hover:** Tooltip shows exact hour, forecast (MW), actual (MW), error (MW)
- **Brush (zoom bar):** Drag to select date range, zoom into specific period
- **Keyboard:** Arrow keys navigate when brush is focused

#### Date Selector (Future Enhancement)
Currently shows full January 2026. Filter by date range planned for future release.

#### Chart Tips
- **Wide red area:** Large forecast errors
- **Blue above green:** Over-forecast (expected more wind than occurred)
- **Green above blue:** Under-forecast (actual wind exceeded forecast)
- **Parallel lines:** Accurate forecasting period

---

### 3. Accuracy Analysis Page

**Purpose:** Deep dive into forecast error patterns and trends.

#### Overall Metrics Card

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **MAE** | mean(\|forecast - actual\|) | Average error magnitude in MW |
| **RMSE** | sqrt(mean((forecast - actual)²)) | Error magnitude with outlier penalty |
| **MAPE** | mean(\|error\| / actual) × 100% | Percentage error (excludes near-zero actuals) |
| **Bias** | mean(forecast - actual) | Directional tendency (+ = over-forecast) |
| **Max Over-forecast** | max(forecast - actual) | Largest single over-prediction (MW) |
| **Max Under-forecast** | min(forecast - actual) | Largest single under-prediction (MW) |
| **Correlation** | Pearson r | Strength of linear relationship (0–1) |

**Reading Correlation:**
- **0.95–1.0:** Excellent agreement
- **0.85–0.95:** Good agreement
- **0.70–0.85:** Moderate agreement
- **<0.70:** Weak agreement (rare for wind forecasts)

#### Daily Metrics Table

**Columns:**
- **Date:** Delivery date (YYYY-MM-DD)
- **MAE (MW):** Daily mean absolute error
- **RMSE (MW):** Daily root mean square error
- **Bias (MW):** Daily bias (+ over, - under)
- **Paired Hours:** Number of hours with both forecast and actual (target: 24)

**Sorting:** Click column headers to sort ascending/descending.

**Use Cases:**
- **Identify worst days:** Sort by MAE descending to find days with largest errors
- **Detect patterns:** Sort by date to see temporal trends
- **Validate completeness:** Check "Paired Hours" column for missing data

#### Error Distribution Histogram

**X-axis:** Error bins (e.g., -3000 to -2500 MW, -2500 to -2000 MW, ...)  
**Y-axis:** Count of hours in each bin  
**Bin width:** 500 MW (configurable via API parameter)

**What to look for:**
- **Centered at zero:** Unbiased forecasts
- **Skewed right:** Tendency to over-forecast
- **Skewed left:** Tendency to under-forecast
- **Wide spread:** High variability in errors
- **Narrow peak:** Consistent accuracy

---

### 4. Procurement Insights Page

**Purpose:** Translate accuracy metrics into actionable intelligence for day-ahead purchasing.

#### Over/Under-Forecast Analysis

**Positive Bias (Over-Forecast):**
- Forecasts predict more wind than actually generated
- **Risk:** Buyers may purchase insufficient traditional generation, relying on wind that doesn't materialize
- **Mitigation:** Add safety margin when forecasts predict high wind

**Negative Bias (Under-Forecast):**
- Forecasts predict less wind than actually generated
- **Risk:** Buyers may over-procure traditional generation, leading to excess costs
- **Mitigation:** Reduce traditional generation purchases when forecasts are conservative

**Zero Bias:**
- Errors cancel out over time
- Individual hours may still have large errors (check RMSE)

#### Top Error Days

**Table:** 5 days with largest MAE, sorted descending.

**Use for:**
- Post-event analysis: What caused large errors on these dates?
- Pattern recognition: Do errors cluster on certain weekdays or weather conditions?
- Trading review: Did procurement decisions account for forecast uncertainty?

#### Risk Assessment

**RMSE Interpretation:**
- **<800 MW:** Low risk, forecasts reliable for day-ahead purchasing
- **800–1,200 MW:** Moderate risk, add 10-15% buffer to wind positions
- **>1,200 MW:** High risk, consider reducing wind reliance or hedging

**Caveats (displayed on page):**
- Historical data only; not predictive of future accuracy
- January wind patterns may differ from other months
- External factors (weather events, grid constraints) not accounted for
- Professional trading advice recommended for actual purchasing decisions

---

### 5. Data Transparency Page

**Purpose:** Understand data sources, methodology, and limitations.

#### Sections (Accordion Format)

**1. Data Sources**
- FUELHH (Actuals): Half-hourly wind generation from Elexon BMRS
- WINDFOR (Forecasts): Hourly wind forecasts from Elexon BMRS
- API base URL: https://data.elexon.co.uk/bmrs/api/v1

**2. Resolution Mismatch**
- WINDFOR: Hourly (60 min)
- FUELHH: Half-hourly (30 min)
- **Solution:** Two consecutive FUELHH half-hours averaged into one hourly value

**3. Forecast Cutoff Logic**
- **Cutoff:** 09:00 UTC on D-1 (day before delivery)
- **Rationale:** N2EX GB day-ahead auction closes ~09:00–09:30 UTC
- **Selection:** Latest WINDFOR run published before cutoff for delivery date

**4. Accuracy Metrics**
- Formulas for MAE, RMSE, MAPE, Bias, Correlation
- Why MAPE excludes near-zero actuals
- Interpretation guidance

**5. Data Completeness**
- 744 expected hours (31 days × 24 hours)
- Actual pairs present
- % completeness

**6. Caveats and Limitations**
- January 2026 only (not representative of other months)
- Historical analysis (not real-time)
- No external factors (weather, grid events)
- Forecast accuracy may vary by forecaster or model version

---

## Common Tasks

### Task 1: Check Overall Accuracy

1. Go to **Dashboard** page
2. Look at **MAE** and **RMSE** cards
3. Compare to typical ranges (MAE 500–1,500 MW, RMSE 700–2,000 MW)
4. Check **Bias** card:
   - Positive → over-forecasts
   - Negative → under-forecasts
   - Near zero → balanced

### Task 2: Find Worst Forecast Days

1. Go to **Accuracy Analysis** page
2. Scroll to **Daily Metrics Table**
3. Click **MAE** column header to sort descending
4. Top rows show days with largest errors
5. Note these dates for further investigation

### Task 3: Visualize a Specific Period

1. Go to **Time Series** page
2. Use **Brush** (zoom bar below main chart) to select date range
3. Drag left/right handles to adjust range
4. Main chart zooms to selected period
5. Hover over lines to see exact values

### Task 4: Understand Forecast Selection

1. Go to **Data Transparency** page
2. Expand **Forecast Cutoff Logic** accordion
3. Read cutoff time (09:00 UTC on D-1) and rationale
4. Example: Jan 15 delivery → forecast selected from Jan 14 before 09:00 UTC

### Task 5: Assess Procurement Risk

1. Go to **Procurement Insights** page
2. Check **Over/Under-Forecast Analysis** section
3. Note bias direction (over/under)
4. Review **Risk Assessment** based on RMSE
5. Apply recommended buffers to day-ahead purchases

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` / `Shift+Tab` | Navigate between interactive elements |
| `Enter` / `Space` | Activate buttons and links |
| `Arrow keys` | Navigate within chart brush |
| `Esc` | Close modal/dialog (if applicable) |

---

## Accessibility Features

- **High Contrast:** Text meets WCAG AA (4.5:1 minimum)
- **Keyboard Navigation:** Full keyboard access to all controls
- **Screen Reader Support:** ARIA labels on charts and icons
- **Responsive Text:** Supports browser zoom up to 200%
- **Color Independence:** Charts use patterns + color (not color alone)

**To enable screen reader:**
- Windows: Narrator (Win + Ctrl + Enter)
- Mac: VoiceOver (Cmd + F5)
- iOS: VoiceOver (Settings > Accessibility)
- Android: TalkBack (Settings > Accessibility)

---

## Troubleshooting

### Dashboard not loading

**Symptom:** Blank page or "Network Error"  
**Causes:**
1. Backend API not running
2. Browser blocking requests (CORS)
3. No internet connection

**Solutions:**
1. Verify backend health: `curl <API_URL>/api/health`
2. Check browser console (F12) for errors
3. Refresh page (Ctrl+R / Cmd+R)
4. Clear browser cache (Ctrl+Shift+Del / Cmd+Shift+Del)

### Charts not rendering

**Symptom:** Chart area empty or shows "Loading..."  
**Causes:**
1. API returned no data
2. JavaScript error in browser
3. Ad blocker interfering

**Solutions:**
1. Open browser DevTools (F12) > Console tab > check for errors
2. Disable ad blockers temporarily
3. Try different browser

### Incorrect data values

**Symptom:** Metrics don't match expected ranges  
**Verification:**
1. Go to **Data Transparency** page
2. Check **Data Completeness** (should be 100%)
3. Verify **Analysis Period** (January 2026)
4. If completeness < 100%, contact administrator

### Mobile layout issues

**Symptom:** Content cut off or horizontal scroll  
**Solutions:**
1. Rotate device to portrait orientation
2. Pinch to zoom out
3. Use desktop browser for full experience

---

## Export and Reporting (Future Enhancement)

**Planned features:**
- Export charts as PNG/SVG
- Export daily metrics table as CSV
- Generate PDF report
- Email scheduled reports

**Current workaround:**
- Screenshot charts (Windows: Win+Shift+S, Mac: Cmd+Shift+4)
- Copy table data to Excel (select, Ctrl+C, paste)
- Use browser print function (Ctrl+P / Cmd+P) for PDF

---

## Data Update Frequency

**Current:** Static historical data (January 2026)  
**No automatic updates.** Dashboard displays pre-computed analysis.

**For live data integration:**
Contact administrator to configure continuous data pipeline.

---

## Browser Storage

**LocalStorage usage:**
- TanStack Query cache (< 5 MB)
- User preferences (future feature)

**To clear storage:**
1. Open DevTools (F12)
2. Application tab > Storage > Local Storage
3. Right-click domain > Clear

---

## Support

### Self-Service
1. Check this User Guide
2. Review **Data Transparency** page in dashboard
3. Read API documentation: `/docs/API.md`

### Contact
- Technical issues: [support email]
- Feature requests: [feature request URL]
- Data questions: [data team contact]

---

## Glossary

| Term | Definition |
|------|------------|
| **MAE** | Mean Absolute Error — average magnitude of forecast errors |
| **RMSE** | Root Mean Square Error — error magnitude with outlier penalty |
| **Bias** | Systematic over/under-forecasting tendency (+ = over, - = under) |
| **MAPE** | Mean Absolute Percentage Error — average % error (excludes zero actuals) |
| **FUELHH** | Elexon dataset: half-hourly actual generation by fuel type |
| **WINDFOR** | Elexon dataset: hourly wind generation forecasts |
| **D-1 Cutoff** | Day-ahead cutoff: 09:00 UTC on the day before delivery |
| **Settlement Period** | 30-minute period in GB electricity market (48 per day) |
| **N2EX** | Nord Pool GB day-ahead auction market |
| **BMRS** | Balancing Mechanism Reporting Service (Elexon) |

---

## Appendix: January 2026 Context

**Why January 2026?**
- Representative winter month (high wind season in UK)
- Complete dataset available (744/744 hours)
- No clock changes (GMT throughout, no BST)
- Historical data allows retrospective analysis

**January 2026 Wind Patterns:**
- Average actual generation: ~14,600 MW
- Range: ~1,000 MW (calm periods) to ~24,000 MW (stormy periods)
- Peak wind typically during Atlantic low-pressure systems
- Lowest wind during high-pressure (anticyclonic) conditions

**Typical January Wind Forecast Accuracy:**
- Industry benchmark MAE: 800–1,200 MW
- Good forecasts: MAE < 800 MW
- Poor forecasts: MAE > 1,500 MW
- This dashboard's results should be compared against these benchmarks

---

## Version History

- **v1.0** (2026-10-26): Initial release
  - Dashboard, Time Series, Accuracy Analysis, Procurement Insights, Data Transparency pages
  - January 2026 data analysis
  - Static deployment

**Planned for v1.1:**
- Date range filters
- CSV export
- PDF report generation
- Comparative analysis (multiple months)
