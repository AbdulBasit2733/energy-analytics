# Known Issues

## Purpose

This document tracks known bugs, limitations, and technical debt in the current release (v1.0). Issues are prioritized by severity and include workarounds where available.

---

## Critical Issues

### None
No critical issues (data loss, security vulnerabilities, or complete feature failures) identified in v1.0.

---

## High Priority Issues

### H1: Recharts Brush Component Unusable on Mobile

**Issue:** Chart zoom/pan brush component (draggable range selector below main chart) is difficult to use on mobile touchscreens.

**Affected Component:** `frontend/src/components/charts/forecast-vs-actual-chart.tsx`

**Impact:**
- Mobile users (~30-40% of potential audience) cannot zoom into specific date ranges
- Must view entire 744-hour dataset at once (cramped visualization)

**Workaround:**
- Brush component hidden on screens <768px (md breakpoint)
- Mobile users can pinch-to-zoom on chart area (limited functionality)
- Recommend using desktop browser for detailed analysis

**Root Cause:** Recharts Brush component not optimized for touch interactions (small hit areas, no touch gestures).

**Proposed Fix:**
- Implement custom touch-friendly zoom controls (date range picker + zoom in/out buttons)
- Alternative: Switch to chart library with better mobile support (e.g., ApexCharts, Highcharts)

**Priority:** High (affects UX for significant user segment)

**Target Release:** v1.1

---

### H2: No Date Range Filters

**Issue:** Dashboard shows full January 2026 (744 hours) with no ability to filter by date range or specific days.

**Affected Pages:** Dashboard, Time Series, Accuracy Analysis

**Impact:**
- Users cannot focus on specific weeks (e.g., "Show me first week of January only")
- Cannot exclude outlier days from metrics calculation
- Chart can be visually cluttered with too much data

**Workaround:**
- Use Brush component (desktop only) to zoom into specific ranges on Time Series chart
- No workaround for filtering aggregated metrics (MAE, RMSE)

**Root Cause:** Scope limitation for v1.0 (16-hour time budget). Date pickers and filter logic deferred.

**Proposed Fix:**
- Add date range picker component (shadcn/ui Calendar + Popover)
- API endpoints already support `from` and `to` query parameters
- Frontend needs UI controls + state management for selected range

**Priority:** High (frequently requested feature based on similar dashboards)

**Target Release:** v1.1

---

## Medium Priority Issues

### M1: TypeScript `baseUrl` Deprecation Warning

**Issue:** TypeScript 5.x emits deprecation warning: "The 'baseUrl' compiler option is deprecated when 'paths' is not specified."

**Affected File:** `frontend/tsconfig.app.json`

**Impact:**
- Console warning during `npm run build` and IDE TypeScript checks
- No runtime effect; cosmetic issue only
- May break in future TypeScript versions (6.0+)

**Workaround:**
- Added `"ignoreDeprecations": "6.0"` to suppress warning
- Alternatively, remove `baseUrl` entirely (requires no path aliases used)

**Root Cause:** Vite + React template includes `baseUrl` by default. TypeScript team deprecated this pattern.

**Proposed Fix:**
- Remove `baseUrl` from tsconfig (verify no path aliases break)
- Or add explicit `paths` mapping if aliases needed

**Priority:** Medium (cosmetic, no functional impact)

**Target Release:** v1.2 (low urgency)

---

### M2: Frontend Bundle Size (~800 KB)

**Issue:** Production frontend bundle size is ~800 KB (gzip), primarily due to Recharts library (~400 KB).

**Affected:** Initial page load performance

**Impact:**
- Larger download on first visit (especially on slow networks)
- LCP (Largest Contentful Paint) still <2.5s, within acceptable range
- Not blocking but suboptimal

**Workaround:**
- Recharts lazy-loaded via dynamic import (reduces blocking impact)
- Browser caching minimizes repeat-load cost

**Root Cause:** Recharts includes entire D3.js dependency tree, no tree-shaking optimization.

**Proposed Fix:**
1. **Short-term:** Audit Recharts imports, ensure only used components imported
2. **Medium-term:** Evaluate lighter alternatives:
   - **visx** (Airbnb, lower-level but smaller)
   - **Chart.js** with react-chartjs-2 wrapper (~200 KB)
   - **Lightweight-charts** (TradingView, fast but limited chart types)

**Priority:** Medium (performance optimization, not blocking)

**Target Release:** v1.2

---

### M3: No Error Recovery for Failed API Calls

**Issue:** If API call fails (network error, backend down), dashboard shows error message but no automatic retry or recovery mechanism.

**Affected:** All pages fetching data via TanStack Query

**Impact:**
- Transient network errors require manual page refresh
- No exponential backoff or retry logic
- Poor UX during network instability

**Workaround:**
- User must manually refresh page (Ctrl+R / Cmd+R)
- TanStack Query provides `refetch()` function but no UI button to trigger it

**Root Cause:** TanStack Query retry disabled (`retry: false` in query options). Intentional for v1.0 to avoid masking backend errors during development.

**Proposed Fix:**
- Enable TanStack Query retry with exponential backoff:
  ```ts
  retry: 3,
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  ```
- Add "Retry" button in error alert component

**Priority:** Medium (affects UX during network issues)

**Target Release:** v1.1

---

### M4: No Export Functionality

**Issue:** Users cannot export charts, tables, or metrics to external formats (CSV, PDF, PNG).

**Affected:** All pages

**Impact:**
- Users must manually screenshot charts (OS screenshot tools)
- Cannot export daily metrics table to Excel for further analysis
- Reduces dashboard utility for reporting workflows

**Workaround:**
- **Charts:** Right-click > "Save image as" (browser built-in, but low quality)
- **Tables:** Select, copy (Ctrl+C), paste into Excel (loses formatting)
- **Metrics:** Manual transcription

**Root Cause:** Export features deferred for v1.0 (time budget constraints).

**Proposed Fix:**
- **CSV export:** Add "Download CSV" button on tables (use `react-csv` or native Blob API)
- **PNG export:** Add "Download Chart" button (use Recharts `toDataURL()` or html2canvas)
- **PDF report:** Generate PDF with jsPDF + backend route

**Priority:** Medium (nice-to-have, workarounds exist)

**Target Release:** v1.2

---

### M5: No Dark Mode

**Issue:** Dashboard supports light mode only. No dark theme or `prefers-color-scheme` detection.

**Affected:** All pages

**Impact:**
- Users preferring dark mode must use browser extensions (e.g., Dark Reader)
- May cause eye strain in low-light environments

**Workaround:**
- Use browser extension (Dark Reader, Night Eye)
- Adjust OS display settings (reduce brightness, enable night mode)

**Root Cause:** Time budget prioritized core functionality over theme variants. Light mode chosen as default for data visualization clarity.

**Proposed Fix:**
- Implement dark mode color palette (desaturated variants, test WCAG AA contrast)
- Add theme toggle button in header
- Respect `prefers-color-scheme` media query
- Store preference in localStorage

**Priority:** Medium (user preference, not accessibility blocker)

**Target Release:** v1.3

---

## Low Priority Issues

### L1: Recharts Tooltip Type Warnings

**Issue:** TypeScript emits type warnings for Recharts tooltip `label` parameter (union type `string | number`, formatter expects `string`).

**Affected File:** `frontend/src/components/charts/forecast-vs-actual-chart.tsx`

**Impact:**
- IDE shows TypeScript warnings (yellow squiggles)
- No runtime errors; types correctly coerced at runtime
- Cosmetic issue for developers only

**Workaround:**
- Cast label to `String(label)` in tooltip formatter
- Or type assertion: `(label: unknown)`

**Current Solution:** Used `String(label)` cast to satisfy TypeScript. Warning suppressed.

**Root Cause:** Recharts types allow `label` to be number (for numeric axes), but datetime axes always produce strings.

**Proposed Fix:**
- No action needed; workaround sufficient
- Could submit PR to Recharts for more precise types

**Priority:** Low (cosmetic, developer QoL only)

**Target Release:** N/A

---

### L2: Skeleton Loader Flash on Fast Networks

**Issue:** On very fast networks (<200ms API response), skeleton loaders flash briefly before content loads, creating visual "jank."

**Affected:** All pages with loading states

**Impact:**
- Slight visual distraction on fast connections
- Not noticeable on typical networks (500ms+ latency)

**Workaround:**
- None needed; acceptable trade-off for loading state visibility

**Root Cause:** TanStack Query shows loading state immediately. No minimum display time for skeleton.

**Proposed Fix:**
- Add minimum skeleton display time (e.g., 500ms) to prevent flash
- Use `useDelayedLoading` hook with 200ms threshold

**Priority:** Low (edge case, minor UX issue)

**Target Release:** v1.3

---

### L3: No Keyboard Shortcuts

**Issue:** Dashboard has no keyboard shortcuts for common actions (e.g., navigate pages, toggle filters, export data).

**Affected:** All pages

**Impact:**
- Power users cannot use shortcuts for efficiency
- Reduces accessibility for keyboard-only users (but full keyboard navigation via Tab works)

**Workaround:**
- Use Tab/Shift+Tab for navigation (functional but slower)
- Use browser shortcuts (Ctrl+R refresh, Ctrl+F find)

**Root Cause:** Keyboard shortcuts deferred for v1.0 (time budget).

**Proposed Fix:**
- Implement global shortcuts with `react-hotkeys-hook`:
  - `Ctrl+1` → Dashboard
  - `Ctrl+2` → Time Series
  - `Ctrl+3` → Accuracy
  - `Ctrl+E` → Export current view
  - `Ctrl+/` → Show keyboard shortcut help

**Priority:** Low (nice-to-have, Tab navigation works)

**Target Release:** v2.0

---

### L4: No User Feedback Mechanism

**Issue:** No in-app feedback form, bug report button, or contact link.

**Affected:** All pages

**Impact:**
- Users cannot report bugs directly from dashboard
- No channel for feature requests or questions
- Relies on external communication (email, GitHub Issues)

**Workaround:**
- Contact support via email (if provided separately)
- Submit GitHub Issue (if repository public)

**Root Cause:** Take-home assignment scope; no support infrastructure.

**Proposed Fix:**
- Add "Send Feedback" button in footer
- Link to Google Form, GitHub Issues, or email
- Or embed in-app form (Formspree, Basin)

**Priority:** Low (external channels work, not user-facing blocker)

**Target Release:** v1.2

---

## Technical Debt

### TD1: No Unit Tests for Frontend Components

**Issue:** Frontend has Vitest setup but no comprehensive component tests written.

**Affected:** All React components

**Impact:**
- Cannot verify component rendering logic automatically
- Regressions detected manually during QA
- Refactoring riskier without test coverage

**Mitigation:**
- TypeScript provides type safety (catches many errors at compile time)
- Manual testing performed on all pages
- Build validation confirms no compilation errors

**Proposed Fix:**
- Write tests for critical components (KPI cards, charts, tables)
- Use React Testing Library + Vitest
- Target 60-70% coverage for components

**Priority:** Medium (improves maintainability)

**Target Release:** v1.2

---

### TD2: Hardcoded API URL in Development

**Issue:** Frontend `api-client.ts` uses hardcoded `http://localhost:8000` for development API base URL (overridden by `VITE_API_URL` env var in production).

**Affected:** `frontend/src/lib/api-client.ts`

**Impact:**
- Requires manual edit to use different backend URL in development
- `.env` file must be created locally

**Mitigation:**
- Vite proxy `/api` → `http://localhost:8000` in dev mode (frontend requests can use relative URLs)
- `.env.example` documents required variables

**Proposed Fix:**
- Always use relative URLs (`/api/...`) in `api-client.ts`
- Remove hardcoded fallback URL

**Priority:** Low (existing pattern works, documented)

**Target Release:** v1.2

---

### TD3: No API Versioning

**Issue:** API endpoints have no version prefix (e.g., `/api/v1/health`). Breaking changes would require client updates.

**Affected:** All API routes

**Impact:**
- Future breaking API changes cannot coexist with old clients
- Must coordinate backend + frontend deployments

**Mitigation:**
- Single client (this dashboard) deployed together with backend
- No external API consumers

**Proposed Fix:**
- Add `/api/v1/` prefix to all routes
- Set up versioned router structure in FastAPI

**Priority:** Low (no external clients, low risk for v1.0)

**Target Release:** v2.0 (if API becomes public)

---

## Documentation Issues

### D1: No Video Walkthrough

**Issue:** User guide is text-only. No video demo or interactive tutorial.

**Affected:** Onboarding experience

**Impact:**
- Users must read full guide to understand features
- No visual walkthrough for first-time users

**Workaround:**
- Follow written USER_GUIDE.md step-by-step
- Explore dashboard pages manually

**Proposed Fix:**
- Record 3-5 minute screen recording showing key features
- Upload to YouTube or embed in README
- Add interactive tooltips for first-time users (Shepherd.js, Intro.js)

**Priority:** Low (documentation sufficient for target users)

**Target Release:** v1.3

---

### D2: No Contribution Guidelines

**Issue:** CONTRIBUTING.md exists but is placeholder only (no detailed guidelines).

**Affected:** Open-source contributors (if repository made public)

**Impact:**
- Contributors unsure of code standards, PR process, testing requirements

**Mitigation:**
- Take-home assignment context (single developer, no external contributors)

**Proposed Fix:**
- Add sections to CONTRIBUTING.md:
  - Code style (ESLint, Prettier, Black)
  - Commit message format
  - PR template
  - Testing requirements
  - Review process

**Priority:** Low (relevant only if open-sourced)

**Target Release:** v1.2

---

## Won't Fix (By Design)

### WF1: No Real-Time Data Updates

**Issue:** Dashboard displays static January 2026 data. No live streaming or automatic updates.

**Justification:**
- **By design:** Historical analysis use case, not real-time monitoring
- Real-time requires websockets, polling, data freshness monitoring (4-6 hour effort)
- Out of scope for take-home assignment

**Status:** Won't fix for v1.x. May revisit for v2.0 if use case evolves to operational monitoring.

---

### WF2: No Multi-User Authentication

**Issue:** No login, user accounts, or role-based access control.

**Justification:**
- **By design:** Historical public data, no sensitive information
- Authentication adds complexity (OAuth, JWT, session management)
- Out of scope for MVP

**Status:** Won't fix for v1.x. May add if dashboard deployed internally with access restrictions.

---

### WF3: No Database

**Issue:** All data stored in-memory (Python dict). No persistent database.

**Justification:**
- **By design:** Small dataset (744 pairs, ~100 KB), read-only access
- Database overkill for this scale
- In-memory faster than any database query

**Status:** Won't fix unless horizontal scaling or multi-month data requires shared state.

---

## Reporting New Issues

### How to Report

1. **Check existing issues:** Review this document to avoid duplicates
2. **Gather details:**
   - Browser + version (Chrome 120, Firefox 121, etc.)
   - OS (Windows 11, macOS, Ubuntu, etc.)
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if visual issue)
3. **Submit via:**
   - GitHub Issues (if repository public)
   - Email: [support contact]
   - Slack: [team channel]

### Issue Template

```markdown
**Summary:** [One-line description]

**Severity:** Critical | High | Medium | Low

**Steps to Reproduce:**
1. Go to [page]
2. Click [button]
3. Observe [behavior]

**Expected:** [What should happen]

**Actual:** [What actually happens]

**Environment:**
- Browser: Chrome 120.0.6099.109
- OS: Windows 11
- Dashboard version: v1.0

**Screenshots:** [Attach if applicable]
```

---

## Document Version

**Version:** 1.0  
**Last Updated:** 2026-10-26  
**Next Review:** Before v1.1 release
