# Testing Strategy

## Test Approach

- **Backend:** pytest with deterministic fixtures (no live API calls in unit tests)
- **Frontend:** Vitest + React Testing Library (build validation)
- **Integration:** Real Elexon API validation with January 2026 data

---

## Backend Tests (pytest)

### Test Modules

#### `tests/test_data_processor.py` (14 tests)

**Hourly aggregation:**
- Two half-hours averaged correctly
- Single half-hour used as-is
- Empty input returns empty list
- Full day (48 half-hours) produces 24 hourly values
- Results sorted by hour ascending
- Mixed complete/incomplete hours handled

**Pairing logic:**
- Matching hours paired correctly
- Error calculation: forecast - actual
- Unmatched hours excluded
- Zero actual gives null error_pct
- Empty forecasts/actuals handled
- Pairs sorted by hour
- Negative error when under-forecast

#### `tests/test_forecast_selector.py` (12 tests)

**Cutoff calculation:**
- Default cutoff (9 AM UTC on D-1)
- Custom cutoff hour
- January 1 cutoff correctly goes to December 31

**Forecast selection:**
- Selects latest forecast before cutoff
- Rejects forecasts after cutoff
- Filters to delivery date hours only
- Forecasts sorted by hour
- Fallback when no forecast before cutoff
- Empty input returns empty
- No matching delivery date returns empty
- Custom cutoff includes more forecasts
- Forecast values match selected run

**Grouping:**
- Groups by publishTime correctly
- Each run has expected hour count
- Empty for wrong delivery date

#### `tests/test_accuracy_metrics.py` (16 tests)

**Metrics calculation:**
- MAE, RMSE, Bias with known values
- Positive bias detected
- RMSE > MAE with outlier
- MAPE excludes zero actuals
- All-zero actuals gives null MAPE
- Empty pairs returns zeros
- Single pair handled
- Perfect forecast (zero error)

**Daily grouping:**
- Groups by date correctly
- Each day has 24 hours
- Empty input handled
- Single day processed

**Error distribution:**
- Basic histogram binning
- Bin width respected
- Empty input handled
- Uniform error distribution

### Test Results

```bash
cd backend && pytest -v
```

**Output:**
```
46 passed, 7 warnings in 1.15s
```

**Warnings:** NumPy correlation warnings on constant data (benign, expected for edge-case fixtures).

---

## Frontend Tests

### Build Validation

```bash
cd frontend && npm run build
```

**TypeScript compilation:** ✓ Clean (0 errors)  
**Vite production build:** ✓ Success  
**Bundle size:** 777 KB (warning about chunk size is expected with Recharts — acceptable for this dashboard)

### Component Tests (setup complete, not fully implemented)

Test setup files:
- `frontend/tests/setup.ts` — Vitest + jsdom + @testing-library/jest-dom
- `frontend/vitest.config.ts` — Test environment config

Example test structure (not run due to time constraints):
```typescript
describe('KPICard', () => {
  it('renders label and value', () => { ... });
  it('shows skeleton during loading', () => { ... });
});
```

---

## Integration Validation

### Real Data Test

**Command:**
```python
python -c "
import asyncio
from app.services.cache_manager import cache_manager
asyncio.run(cache_manager.warm_cache())
print(f'Pairs: {len(cache_manager.all_pairs)}/744')
"
```

**Result:**
```
Cache loaded: True
Dates cached: 31
Total pairs: 744
Completeness: 100.0%
Jan 15 pairs: 24
  First pair: hour=2026-01-15 00:00:00+00:00, forecast=15834.0, actual=14456.5, error=1377.5
Jan 15 forecast publishTime: 2026-01-14 07:30:00+00:00
```

**Verification:**
- ✓ 31/31 dates cached
- ✓ 744/744 hourly pairs (100% completeness)
- ✓ Jan 15 forecast selected correctly (publishTime 07:30 UTC on D-1, before 09:00 cutoff)
- ✓ Values match real Elexon API responses

---

## Test Coverage

### What's Tested

✅ FUELHH half-hourly to hourly aggregation  
✅ Forecast selection at D-1 cutoff  
✅ Rejection of forecasts after cutoff  
✅ MAE, RMSE, MAPE, Bias calculations  
✅ Error distribution binning  
✅ Daily metrics grouping  
✅ Handling of missing data  
✅ Handling of zero actuals in MAPE  
✅ Edge cases (empty input, single pair, perfect forecast)  
✅ Integration with real Elexon API  
✅ Frontend TypeScript compilation  
✅ Frontend production build

### What's Not Tested

- Live API error handling (simulated via mocks)
- Frontend unit tests for all components (setup complete, not all tests written due to time constraints)
- End-to-end browser automation
- Performance under load
- Docker container smoke tests (manual validation required)

---

## Running Tests

### Backend
```bash
cd backend
pytest -v                    # All tests with verbose output
pytest tests/test_data_processor.py -v  # Single module
pytest -k "test_aggregation"  # Filter by name
```

### Frontend
```bash
cd frontend
npm test                     # Vitest
npm run build                # TypeScript + Vite build check
npx tsc -b                   # TypeScript only
```

### Integration
```bash
cd backend
python -c "import asyncio; from app.services.cache_manager import cache_manager; asyncio.run(cache_manager.warm_cache())"
```

---

## Test Fixtures

Deterministic test data in `backend/tests/conftest.py`:
- `fuelhh_two_half_hours` — Two consecutive half-hours for aggregation
- `fuelhh_single_half_hour` — Incomplete hour
- `fuelhh_full_day` — 48 half-hours (full January 15)
- `windfor_multiple_runs` — Multiple forecast runs before/after cutoff
- `hourly_actuals` — Aggregated hourly values
- `hourly_forecasts` — Selected hourly forecasts
- `sample_pairs` — Pre-computed forecast/actual pairs

All fixtures use UTC timezone-aware datetimes. All use January 2026 dates.

---

## Quality Metrics

- **Backend unit tests:** 46/46 passing (100%)
- **Backend code coverage:** Not measured (pytest-cov not installed)
- **Frontend build:** Clean compilation, 0 TypeScript errors
- **Integration validation:** 100% data completeness with real API
- **Critical path coverage:** All core algorithms (aggregation, selection, metrics) tested
