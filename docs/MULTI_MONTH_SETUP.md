# Multi-Month Data Setup Guide

**Status:** ✅ Frontend Ready | ⚠️ Backend Configuration Required  
**Date:** 2026-10-26

---

## 🎯 **What Changed**

The frontend date picker now supports:
- ✅ All 12 months of 2026 (Jan-Dec)
- ✅ Quarterly ranges (Q1-Q4)
- ✅ Full year 2026
- ✅ Custom date range selection

**However**, the backend currently only has **January 2026** data pre-cached.

---

## ⚠️ **Current Limitation**

When you select **October 2026** (or any month except January):

```
User selects: October 2026
Frontend → API: GET /api/dashboard/kpis?from=2026-10-01&to=2026-10-31
Backend: Filters cache for October dates
Result: Empty data (no pairs found)
```

**Why?** Backend cache is only populated for January 2026 at startup.

---

## 🔧 **Solution: Enable Multiple Months**

### **Option 1: Environment Variable (Quick & Easy)**

**Step 1:** Edit `backend/.env`:

```bash
# Before (January only):
ANALYSIS_MONTH=2026-01

# After (January + October):
ANALYSIS_YEAR=2026
CACHE_MONTHS=01,10

# Or cache all months:
CACHE_MONTHS=01,02,03,04,05,06,07,08,09,10,11,12
```

**Step 2:** Update `backend/app/config.py`:

```python
class Settings(BaseSettings):
    analysis_year: int = Field(default=2026, env="ANALYSIS_YEAR")
    analysis_month: int = Field(default=1, env="ANALYSIS_MONTH")
    
    # NEW: Support multiple months
    cache_months: str = Field(default="01", env="CACHE_MONTHS")
    
    @property
    def months_to_cache(self) -> list[int]:
        """Parse comma-separated months into list of integers."""
        return [int(m) for m in self.cache_months.split(",")]
```

**Step 3:** Update `backend/app/services/cache_manager.py`:

```python
async def warm_cache(self):
    """Warm cache for all configured months."""
    if self._loaded:
        return
    
    logger.info("Warming cache for months: %s", settings.cache_months)
    
    for month in settings.months_to_cache:
        await self._warm_month(settings.analysis_year, month)
    
    self._loaded = True
    logger.info("Cache warmed: %d dates, %d pairs", 
                self.dates_cached, len(self._pairs))

async def _warm_month(self, year: int, month: int):
    """Fetch and cache data for a single month."""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    logger.info("Fetching data for %s-%02d...", year, month)
    
    # Existing cache warming logic here...
    # (Same as current warm_cache implementation)
```

**Step 4:** Restart backend:

```bash
cd backend
uvicorn app.main:app --reload
```

**Result:** Backend now caches January + October (or all months if configured).

---

### **Option 2: On-Demand Fetching (Advanced)**

Modify cache manager to fetch data on-demand when requested month is not cached:

```python
async def get_pairs_for_range(
    self, 
    start: date | None = None, 
    end: date | None = None
) -> list[ForecastActualPair]:
    """Get pairs for date range, fetching if not cached."""
    
    # Check if requested range is cached
    if start and end:
        required_months = self._get_month_range(start, end)
        cached_months = self._get_cached_months()
        
        missing_months = required_months - cached_months
        if missing_months:
            logger.info("Fetching missing months: %s", missing_months)
            for year, month in missing_months:
                await self._warm_month(year, month)
    
    # Existing filtering logic...
    if start is None and end is None:
        return self._pairs
    
    filtered = []
    for p in self._pairs:
        dt = p.hour.date()
        if start and dt < start:
            continue
        if end and dt > end:
            continue
        filtered.append(p)
    
    return filtered
```

**Pros:**
- ✅ No manual configuration needed
- ✅ Fetches data automatically when user selects new month
- ✅ Best user experience

**Cons:**
- ⚠️ First request for new month will be slow (10-30 seconds)
- ⚠️ Requires Elexon API to have historical data for that month
- ⚠️ More complex code

---

## 📊 **Data Availability**

### **Historical Data (Past Months)**

Elexon BMRS API typically retains:
- ✅ **Recent months (1-3 months):** Full historical data available
- ⚠️ **Older months (3-12 months):** May be available but slower
- ❌ **Very old data (>1 year):** May not be available or require Archive API

### **Future Months**

For months that haven't occurred yet (e.g., selecting October 2026 in January 2026):
- ❌ **Actuals (FUELHH):** Not available (hasn't happened yet)
- ✅ **Forecasts (WINDFOR):** May be available for near-term (D+1, D+7)

**Recommendation:** Only cache and analyze **completed months** (past months with full actual data).

---

## 🧪 **Testing Multi-Month Setup**

### **Test Plan:**

**1. Verify January (Already Cached):**
```bash
curl "http://localhost:8000/api/dashboard/kpis?from=2026-01-01&to=2026-01-31"
# Should return 744 pairs (31 days × 24 hours)
```

**2. Add October to Config:**
```bash
# backend/.env
CACHE_MONTHS=01,10
```

**3. Restart Backend & Check Logs:**
```bash
uvicorn app.main:app --reload

# Expected logs:
# INFO: Warming cache for months: 01,10
# INFO: Fetching data for 2026-01...
# INFO: Fetching data for 2026-10...
# INFO: Cache warmed: 62 dates, 1488 pairs (31 Jan + 31 Oct)
```

**4. Test October Endpoint:**
```bash
curl "http://localhost:8000/api/dashboard/kpis?from=2026-10-01&to=2026-10-31"
# Should return 744 pairs (31 days × 24 hours)
```

**5. Test Frontend:**
```
1. Open dashboard: http://localhost:5173
2. Click date dropdown
3. Select "October 2026"
4. Verify KPIs update (not all zeros)
5. Check charts show data
```

---

## 📝 **Example: Cache All 2026 Months**

### **Configuration:**

**backend/.env:**
```bash
ANALYSIS_YEAR=2026
CACHE_MONTHS=01,02,03,04,05,06,07,08,09,10,11,12
```

### **Expected Behavior:**

**Startup Time:**
- 12 months × ~10 seconds each = **~2 minutes** initial cache warm
- Subsequent starts: Load from disk cache (~5 seconds)

**Memory Usage:**
- 1 month = ~1,500 pairs × 200 bytes = **~300 KB**
- 12 months = **~3.6 MB** (acceptable)

**Cache Eviction:**
- Cache manager keeps max 12 months (configurable via `_max_cached_months`)
- Oldest months evicted automatically if limit exceeded

---

## 🚀 **Production Deployment**

### **Recommended Configuration:**

**For Assignment (January 2026 only):**
```bash
CACHE_MONTHS=01
```
- Fast startup (10 seconds)
- Meets assignment requirements
- 100% data completeness

**For Real Production (Rolling 12 months):**
```bash
CACHE_MONTHS=01,02,03,04,05,06,07,08,09,10,11,12
```
- Slower startup (~2 min first time, then cached)
- Full year analysis capability
- Supports quarter-over-quarter comparison

**For Demo (January + October for comparison):**
```bash
CACHE_MONTHS=01,10
```
- Shows multi-month capability
- Fast startup (20 seconds)
- Good for video demo

---

## 🐛 **Troubleshooting**

### **Problem: "No data for October"**

**Symptoms:**
- Frontend shows October selected
- KPIs show all zeros
- Charts are empty

**Diagnosis:**
```bash
curl "http://localhost:8000/api/health"
# Check: dates_cached should include October dates
```

**Solutions:**
1. Check `CACHE_MONTHS` includes `10`
2. Restart backend: `uvicorn app.main:app --reload`
3. Check backend logs for cache warming
4. Verify Elexon API has October 2026 data:
   ```bash
   curl "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream?\
   settlementDateFrom=2026-10-01&settlementDateTo=2026-10-31&fuelType=WIND"
   ```

### **Problem: "Slow first load for new month"**

**Expected:** First request for uncached month takes 10-30 seconds

**Solutions:**
1. Pre-cache all expected months in `CACHE_MONTHS`
2. Implement Option 2 (on-demand fetching) with loading indicator
3. Add frontend loading message: "Fetching October data from Elexon..."

### **Problem: "Cache taking too much memory"**

**Symptoms:**
- Docker container killed (OOM)
- High memory usage in production

**Solutions:**
1. Reduce `_max_cached_months` in cache_manager.py:
   ```python
   self._max_cached_months = 6  # Keep only 6 months
   ```
2. Clear old months manually:
   ```bash
   rm -rf backend/cache/*.json
   ```
3. Increase Docker memory limit in docker-compose.yml:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 2G  # Increase from 1G
   ```

---

## 📈 **Performance Metrics**

| Months Cached | Startup Time | Memory Usage | API Response Time |
|---------------|--------------|--------------|-------------------|
| 1 (January) | ~10s | ~300 KB | <100ms |
| 2 (Jan + Oct) | ~20s | ~600 KB | <100ms |
| 12 (Full year) | ~2 min | ~3.6 MB | <100ms |

**Note:** Startup time is only for first run. Subsequent starts load from disk cache (~5s).

---

## ✅ **Acceptance Criteria**

### **Minimal (Assignment Submission):**
- [x] Frontend supports all 12 months
- [x] Backend caches January 2026
- [x] Date picker shows all months (frontend-ready)
- [x] Documented how to enable other months

### **Recommended (Video Demo):**
- [ ] Backend caches January + October
- [ ] Video shows switching between months
- [ ] Demonstrates quarter-over-quarter comparison

### **Production-Ready:**
- [ ] Backend caches all 12 months of 2026
- [ ] On-demand fetching for uncached months
- [ ] Loading indicators for slow fetches
- [ ] Error handling for unavailable months

---

## 🎬 **Video Demo Script (Multi-Month)**

```
"The date picker supports all 12 months of 2026,
plus quarterly and full-year views.

[Click October 2026]

For the demo, I've pre-cached January and October.
This shows how the system scales to multi-month analysis.

[Show KPIs update]

In production, you can configure which months to cache
via environment variables, or fetch on-demand as users
select different periods.

This flexibility is critical for electricity procurement
analysts who need to compare seasonal patterns - 
winter wind vs summer wind, for example."
```

---

## 🔗 **Related Documentation**

- [DATE_PICKER_FEATURE.md](DATE_PICKER_FEATURE.md) - Frontend date picker implementation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) - Current limitations

---

**Document Version:** 1.0  
**Last Updated:** 2026-10-26  
**Status:** Ready for Implementation  
**Estimated Implementation Time:** 30-60 minutes
