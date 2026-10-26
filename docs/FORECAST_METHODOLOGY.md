# Forecast Methodology

## Day-Ahead Cutoff Definition

### What is the Cutoff?

The **forecast cutoff** is the deadline by which a wind forecast must be available for use in day-ahead electricity procurement decisions.

For this analysis: **09:00 UTC on D-1** (the day before delivery).

### Why 09:00 UTC?

The N2EX (Nord Pool) GB day-ahead half-hourly auction typically closes around **09:00–09:30 UK time** on D-1. During January (GMT), UK time = UTC, so this is **09:00–09:30 UTC**.

Procurement analysts must submit bids before gate closure. Therefore, they can only use forecasts published **before ~09:00 UTC** on D-1.

**Source:** Established industry practice for GB day-ahead market. The precise gate closure time is subject to Nord Pool's operational rules.

### Configurable

The cutoff hour is configurable via the `FORECAST_CUTOFF_HOUR` environment variable (default: 9).

---

## Forecast Selection Algorithm

For each delivery date D, select the **most recent** WINDFOR forecast run published **before** the cutoff.

### Algorithm Steps

```
Input: delivery_date (e.g., 2026-01-15), all_forecasts (WINDFOR records), cutoff_hour (default 9)

1. Compute cutoff datetime:
   day_before = delivery_date - 1 day
   cutoff = datetime(day_before.year, day_before.month, day_before.day, cutoff_hour, 0, 0, UTC)
   # For Jan 15: cutoff = 2026-01-14 09:00:00 UTC

2. Define delivery period:
   delivery_start = datetime(delivery_date.year, delivery_date.month, delivery_date.day, 0, 0, 0, UTC)
   delivery_end = delivery_start + 23 hours
   # For Jan 15: 2026-01-15 00:00 to 2026-01-15 23:00 UTC

3. Filter eligible forecasts:
   eligible = [f for f in all_forecasts
               if f.publishTime < cutoff
               and delivery_start <= f.startTime <= delivery_end]

4. If no eligible forecasts:
   fallback to earliest available forecast (flag as fallback)

5. Group by publishTime to identify distinct forecast runs

6. Select the run with MAX(publishTime)

7. Return all hourly forecasts from that run for the delivery date (≤24 records)
```

### Worked Example: January 15, 2026

**Delivery date:** 2026-01-15  
**Cutoff:** 2026-01-14 09:00:00 UTC

**Available forecast runs** (example):
- Run A: publishTime = 2026-01-14 02:30 UTC ✓ (before cutoff)
- Run B: publishTime = 2026-01-14 04:30 UTC ✓ (before cutoff)
- Run C: publishTime = 2026-01-14 07:30 UTC ✓ (before cutoff, **latest**)
- Run D: publishTime = 2026-01-14 09:30 UTC ✗ (after cutoff — rejected)

**Selected:** Run C (publishTime = 2026-01-14 07:30 UTC)

Each run contains ~73 hourly forecasts covering ~3 days ahead. We extract only the 24 forecasts for hours 2026-01-15 00:00 through 2026-01-15 23:00.

**Verified against real data:** For January 15, the API returned 11 forecast runs. The algorithm correctly selected the run published at 07:30 UTC on Jan 14.

---

## Half-Hourly to Hourly Aggregation

### The Resolution Mismatch

- **FUELHH (actuals):** Half-hourly resolution (30 min)
- **WINDFOR (forecasts):** Hourly resolution (60 min)

Direct comparison requires matching temporal resolution.

### Aggregation Method

**Average two consecutive half-hours into one hourly value.**

```
For each hour H (00:00, 01:00, ..., 23:00):
  Find all FUELHH records where floor(startTime to hour) = H
  If 2 records found:
    hourly_actual = average(gen1, gen2)
  If 1 record found:
    hourly_actual = gen1
    (flag as incomplete with half_hour_count = 1)
```

### Mapping Table

| Hour | Settlement Periods | FUELHH startTime | Aggregation |
|------|-------------------|------------------|-------------|
| 00:00 | 1, 2 | 00:00, 00:30 | average(SP1, SP2) |
| 01:00 | 3, 4 | 01:00, 01:30 | average(SP3, SP4) |
| 02:00 | 5, 6 | 02:00, 02:30 | average(SP5, SP6) |
| ... | ... | ... | ... |
| 23:00 | 47, 48 | 23:00, 23:30 | average(SP47, SP48) |

### Why Not Duplicate?

Alternative approach: duplicate WINDFOR hourly value for both half-hours.

**Rejected** because:
- Artificially inflates sample size
- Misrepresents actual 30-minute variation
- Averaging two actuals to one hourly value preserves actual energy generation more accurately

---

## Forecast Accuracy Metrics

### Definitions

All metrics computed on **matched hourly pairs only** — hours where both forecast and actual exist.

Let:
- N = number of matched pairs
- f_i = forecast for hour i
- a_i = actual for hour i
- e_i = f_i - a_i (error)

#### MAE (Mean Absolute Error)
```
MAE = (1/N) × Σ|e_i|
```
**Units:** MW  
**Interpretation:** Average magnitude of errors regardless of direction.

#### RMSE (Root Mean Square Error)
```
RMSE = sqrt((1/N) × Σ(e_i²))
```
**Units:** MW  
**Interpretation:** Penalizes large errors more heavily. RMSE ≥ MAE always.

#### Bias (Mean Error)
```
Bias = (1/N) × Σe_i = (1/N) × Σ(f_i - a_i)
```
**Units:** MW  
**Sign Convention:**
- Positive bias → forecasts tend to **over-predict**
- Negative bias → forecasts tend to **under-predict**
- Zero bias → no systematic tendency (errors cancel out)

#### MAPE (Mean Absolute Percentage Error)
```
MAPE = (100/N) × Σ(|e_i| / a_i)   [where a_i > threshold]
```
**Units:** %  
**Exclusion Rule:** Hours where a_i ≤ 1 MW are **excluded** to avoid division by near-zero.

**MAPE Limitations:**
- Explodes to infinity when actual generation is very low
- Asymmetric: over-forecasts and under-forecasts treated differently
- Not suitable for wind data during calm periods (near-zero generation)
- Use MAE and RMSE as primary metrics; MAPE as supplementary

#### Correlation (Pearson)
```
r = cov(f, a) / (σ_f × σ_a)
```
**Range:** -1 to +1  
**Interpretation:** Strength of linear relationship. r ≈ 1 indicates strong positive correlation.

---

## Missing Data Handling

- **No imputation:** Missing values are never filled or interpolated
- **Pairing rule:** Only matched hours are included in metrics
- **Completeness reported:** % of expected hourly pairs present
- **Expected:** 31 days × 24 hours = 744 hourly pairs for January

**Actual result:** 744/744 pairs (100% completeness) for January 2026.

---

## Timezone and Daylight Saving

- **January 2026:** GMT (UTC+0). No offset.
- All comparisons in UTC.
- British Summer Time (BST, UTC+1) applies March 29 – October 25, 2026 (not relevant).
- No clock-change days in January (always 48 half-hour periods per day).

---

## Data Quality Rules

1. **Forecast must precede delivery:** `publishTime < startTime` always
2. **Forecast must be published before cutoff:** `publishTime < cutoff_datetime`
3. **Actuals published after delivery:** `publishTime` typically 30 min after `startTime`
4. **No synthetic data:** All values from real Elexon BMRS API responses
5. **Cache validation:** First-fetch values persisted; subsequent loads from cache
6. **Test validation:** 46 automated tests verify selection, aggregation, and metric logic

---

## Example Calculation

### Data
**Delivery date:** 2026-01-15, hour 00:00  
**Forecast (WINDFOR):** 15,834 MW (published 2026-01-14 07:30 UTC)  
**Actual (FUELHH):**
- SP1 (00:00–00:30): 14,850 MW
- SP2 (00:30–01:00): 14,063 MW
- **Hourly average:** (14,850 + 14,063) / 2 = **14,456.5 MW**

### Error Metrics
```
error = 15,834 - 14,456.5 = +1,377.5 MW (over-forecast)
abs_error = 1,377.5 MW
error_pct = (1,377.5 / 14,456.5) × 100 = 9.53%
```

**Interpretation:** Forecast exceeded actual by 1,378 MW (~10%). The utility expected more wind on the system than materialized.

---

## References

- Elexon BMRS API Documentation: https://bmrs.elexon.co.uk/api-documentation
- Nord Pool (N2EX) day-ahead market
- Balancing and Settlement Code (BSC) for GB electricity market
