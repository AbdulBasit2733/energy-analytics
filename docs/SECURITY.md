# Security

## Security Posture

This document outlines security considerations, threat model, and best practices for the UK Wind Forecast Accuracy Dashboard.

**Risk Level:** LOW  
**Justification:** Historical public data only, no user authentication, read-only operations, no sensitive information.

---

## Threat Model

### Assets

| Asset | Sensitivity | Impact if Compromised |
|-------|-------------|----------------------|
| Elexon BMRS data | Public | None (already public) |
| Backend API | Low | Service disruption only |
| Frontend static files | Low | Defacement, no data loss |
| Cache files | Low | Performance degradation (refetch from Elexon) |
| Environment variables | Medium | CORS bypass, Elexon API abuse |

### Threat Actors

1. **Script Kiddies:** Automated vulnerability scanners, random attack attempts
2. **Competitors:** Reconnaissance on tech stack and methodology (low impact)
3. **Malicious Users:** DDoS attempts, cache poisoning

**No High-Value Targets:** No user data, financial transactions, or proprietary algorithms.

---

## Authentication & Authorization

### Current State: No Authentication

**Decision:** v1.0 has no login, user accounts, or access control.

**Justification:**
- Historical public data (Elexon BMRS is open-access)
- Read-only dashboard (no writes, no state changes)
- Take-home assignment scope

**Risks:**
- Anyone with URL can access dashboard
- No usage tracking per user
- No role-based views (all users see everything)

**Mitigation:**
- Deploy behind corporate VPN if internal use only
- Add IP whitelist at load balancer level
- Consider HTTP Basic Auth for simple password protection

**Future Enhancement (v2.0):**
- OAuth 2.0 / OIDC (Google Workspace, Azure AD)
- JWT-based authentication
- Role-based access control (admin, analyst, read-only)

---

## Data Security

### Data Classification

| Data Type | Classification | Encryption | Storage |
|-----------|---------------|------------|---------|
| FUELHH/WINDFOR raw data | Public | Not required | Cache (JSON files) |
| Derived metrics (MAE, RMSE) | Public | Not required | In-memory |
| API responses | Public | HTTPS in transit | None |
| Environment variables | Internal | Not encrypted at rest | .env files (excluded from Git) |

### Data in Transit

**Protocol:** HTTPS/TLS 1.3 (production)

**Backend ↔ Elexon API:**
- HTTPS enforced (`https://data.elexon.co.uk`)
- Elexon API has no authentication (public access)
- No API keys or tokens required

**Frontend ↔ Backend:**
- Development: HTTP (localhost only, acceptable)
- Production: HTTPS enforced via redirect (nginx/load balancer)
- CORS headers restrict origin to frontend domain

**Recommendation:** Force HTTPS in production with HSTS header:
```python
# backend/app/main.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### Data at Rest

**Cache Files:**
- Location: `backend/cache/*.json`
- Contents: Public Elexon data (FUELHH, WINDFOR responses)
- Encryption: Not required (public data)
- Permissions: OS-level file permissions (owner read/write only)

**No Database:** All data in-memory or cache files. No persistent user data.

---

## API Security

### CORS (Cross-Origin Resource Sharing)

**Configuration:**
```python
# backend/app/main.py
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

**Security Considerations:**
- ✅ Specific origins only (not `*`)
- ✅ GET methods only (no POST/PUT/DELETE in v1.0)
- ✅ Credentials allowed (for future auth)
- ⚠️ `allow_headers=["*"]` acceptable for public API (no sensitive headers)

**Recommendation:** In production, set `CORS_ORIGINS` to exact frontend URL:
```bash
CORS_ORIGINS=https://dashboard.example.com
```

### Rate Limiting

**Current State:** No rate limiting on backend API.

**Justification:**
- Single tenant (internal dashboard)
- Elexon API has no documented rate limits
- Cache eliminates Elexon API dependency after first fetch

**Risks:**
- Public deployment vulnerable to DDoS
- Malicious user could spam API, increasing backend load

**Recommendation (for public deployment):**
- Add rate limiting middleware (slowapi, Flask-Limiter equivalent for FastAPI):
  ```python
  from slowapi import Limiter, _rate_limit_exceeded_handler
  from slowapi.util import get_remote_address

  limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
  ```
- Limit: 100 requests/minute per IP (adjust based on usage)
- Exempt health check endpoint (`/api/health`)

### Input Validation

**Query Parameters:**
- All user inputs validated via Pydantic models
- Date formats: ISO 8601 (YYYY-MM-DD) enforced
- Integer ranges: Checked (e.g., bin_width > 0)
- SQL injection: N/A (no database queries)
- Command injection: N/A (no shell commands from user input)

**Example:**
```python
# backend/app/routers/timeseries.py
from pydantic import Field
from datetime import date

class TimeSeriesParams(BaseModel):
    date: date | None = None  # Pydantic validates YYYY-MM-DD format
    from_date: date | None = Field(None, alias="from")
    to_date: date | None = Field(None, alias="to")
```

**Security:** Pydantic validation prevents type confusion attacks.

### Error Responses

**Current Behavior:**
- 400: Invalid query parameters (e.g., malformed date)
- 404: Resource not found (e.g., no data for requested date)
- 500: Internal server error

**Security Consideration:** Do not leak stack traces or internal paths in production.

**Recommendation:** Set FastAPI debug mode based on environment:
```python
# backend/app/main.py
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
app = FastAPI(debug=DEBUG)
```

Production: `DEBUG=false` → Generic error messages only.

---

## Dependency Security

### Backend (Python)

**Requirements:** `backend/requirements.txt`

**Key Dependencies:**
- fastapi==0.162.0
- uvicorn==0.34.0
- httpx==0.28.1
- pydantic==2.10.5
- pandas==2.2.3
- numpy==2.2.1

**Vulnerability Scanning:**
```bash
cd backend
pip install pip-audit
pip-audit
```

**Result (as of 2026-10-26):** No known vulnerabilities.

**Recommendation:**
- Run `pip-audit` monthly
- Update dependencies quarterly (test before production)
- Subscribe to GitHub security advisories for critical packages

### Frontend (JavaScript)

**Dependencies:** `frontend/package.json`

**Key Dependencies:**
- react==19.3.1
- vite==8.3.4
- @tanstack/react-query==5.64.2
- recharts==3.10.1

**Vulnerability Scanning:**
```bash
cd frontend
npm audit
```

**Result (as of 2026-10-26):** No high/critical vulnerabilities. 2 moderate (in transitive deps, no exploitable path).

**Recommendation:**
- Run `npm audit fix` monthly
- Avoid `npm audit fix --force` (can break builds)
- Review advisories for exploitability (many are false positives for build-time deps)

---

## Infrastructure Security

### Docker

**Base Images:**
- Backend: `python:3.12-slim` (official Python, security patches from Debian team)
- Frontend: `node:22-alpine` (build), `nginx:alpine` (serve)

**Security Best Practices:**
- ✅ Use official images (not community-maintained)
- ✅ Pin specific versions (not `latest`)
- ✅ Multi-stage builds (node_modules not in final image)
- ✅ Non-root user in containers (nginx runs as `nginx` user)

**Recommendation:**
- Scan images with Trivy or Docker Scout:
  ```bash
  docker scout cves uk-energy-backend:latest
  ```
- Rebuild images monthly to pick up base image patches

### Environment Variables

**Secrets Management:**

**Current State:** `.env` files (excluded from Git via `.gitignore`).

**Production Deployment:**
- Railway / Render: Use platform secret manager (encrypted at rest)
- AWS ECS: Use AWS Secrets Manager or Parameter Store
- Never commit `.env` to Git

**Environment Variable Types:**

| Variable | Sensitivity | Storage |
|----------|-------------|---------|
| `ELEXON_BASE_URL` | Public | Plain text OK |
| `FORECAST_CUTOFF_HOUR` | Public | Plain text OK |
| `CORS_ORIGINS` | Internal | Plain text OK |
| `DEBUG` | Internal | Plain text OK |
| Future: API keys | Secret | Encrypted secret manager |

**No High-Sensitivity Secrets in v1.0** (Elexon API is public, no auth).

### Network Security

**Firewall Rules (Production):**
- Allow inbound: 443 (HTTPS), 80 (HTTP redirect to 443)
- Deny all other inbound ports
- Outbound: Allow 443 to Elexon API (`data.elexon.co.uk`)

**VPC (AWS) / Private Network:**
- Backend and frontend can be in same VPC
- Backend does not need public IP (ALB/proxy handles traffic)
- Elexon API requires outbound internet (NAT gateway)

---

## Application Security

### XSS (Cross-Site Scripting)

**Risk:** Low (all data from trusted source: Elexon API)

**Mitigation:**
- React escapes user input by default
- No `dangerouslySetInnerHTML` used
- No user-generated content displayed

**Recommendation:** Add Content Security Policy (CSP) header:
```nginx
# frontend/nginx.conf
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;" always;
```

### CSRF (Cross-Site Request Forgery)

**Risk:** None (read-only API, no state-changing operations)

**Future (if POST/PUT/DELETE added):** Implement CSRF tokens or SameSite cookies.

### SQL Injection

**Risk:** None (no database, no SQL queries)

### Command Injection

**Risk:** None (no shell commands executed from user input)

### Path Traversal

**Risk:** Low

**Mitigation:**
- No file uploads
- No user-controlled file paths
- Cache directory access limited to backend process

### Denial of Service (DoS)

**Risk:** Medium (public deployment vulnerable to request flooding)

**Mitigation:**
- Rate limiting (see API Security section)
- Backend cache reduces load (no repeated Elexon API calls)
- Use CDN (Cloudflare) for DDoS protection (future)

---

## Logging and Monitoring

### Current State

**Backend Logs:** Uvicorn stdout/stderr (HTTP requests, errors)

**Frontend Logs:** Nginx access/error logs (if using nginx)

**No Centralized Logging:** Logs not aggregated or monitored.

**Recommendation (Production):**
1. **Aggregate logs:** Send to CloudWatch, Datadog, or ELK stack
2. **Monitor for:**
   - HTTP 500 errors (backend failures)
   - HTTP 429 errors (rate limit exceeded, possible attack)
   - Unusual traffic spikes (potential DDoS)
3. **Alert on:**
   - Backend health check failures
   - Cache load failures
   - Sustained error rates >5%

**Example (AWS CloudWatch):**
- ECS/Fargate automatically sends container logs to CloudWatch
- Set alarm: `HTTP 5xx count > 10 in 5 minutes` → SNS notification

### Sensitive Data in Logs

**Current State:** No PII or secrets logged.

**Best Practices:**
- Never log passwords, API keys, or tokens
- Redact user input in logs (future if user auth added)
- Use structured logging (JSON format) for easy parsing

---

## Incident Response

### Security Incident Types

1. **Data Breach:** N/A (no sensitive data stored)
2. **Service Disruption:** DDoS, cache deletion, backend crash
3. **Unauthorized Access:** N/A (no authentication to bypass)
4. **Dependency Vulnerability:** High/critical CVE in package

### Response Procedures

**1. Detect:**
- Monitor health check endpoint (`/api/health`)
- Alert on sustained 500 errors or downtime

**2. Assess:**
- Check backend logs for error cause
- Verify cache integrity (`ls backend/cache/*.json`)
- Check Elexon API status (external dependency)

**3. Contain:**
- If DDoS: Enable rate limiting or Cloudflare proxy
- If cache corruption: Delete cache, restart backend (refetches from Elexon)
- If dependency vuln: Assess exploitability (CVSS score, attack vector)

**4. Remediate:**
- Apply patches (`pip install -U <package>`, `npm update <package>`)
- Rebuild Docker images with updated deps
- Redeploy to production

**5. Document:**
- Log incident in `KNOWN_ISSUES.md`
- Update this SECURITY.md if new threat identified

### Rollback Plan

**Scenario:** New deployment introduces security issue.

**Steps:**
1. Railway/Render: Rollback to previous deployment via dashboard
2. Docker: `git checkout <previous-commit>`, `docker compose up --build`
3. AWS ECS: Update service to use previous task definition revision

**RTO (Recovery Time Objective):** <15 minutes  
**RPO (Recovery Point Objective):** No data loss (cache persists, can refetch from Elexon)

---

## Compliance

### GDPR (General Data Protection Regulation)

**Applicability:** Not applicable.

**Justification:**
- No personal data collected (no users, no accounts)
- No cookies beyond session (TanStack Query cache in localStorage, no PII)
- No data processing of EU citizens' personal information

**If User Auth Added (Future):** GDPR compliance required:
- Privacy policy
- Cookie consent banner
- Data retention policies
- Right to erasure (delete account)

### WCAG 2.2 AA (Accessibility)

**Compliance Status:** Target met (not legally required but best practice).

**Audited:**
- Color contrast: 4.5:1 minimum ✓
- Keyboard navigation: Full access ✓
- Screen reader support: ARIA labels ✓
- Focus indicators: Visible ✓

**Evidence:** `docs/UI_UX_DESIGN_SYSTEM.md` — Accessibility section

---

## Security Checklist

### Pre-Deployment

- [ ] HTTPS enforced (redirect HTTP → HTTPS)
- [ ] CORS configured with specific origins (not `*`)
- [ ] DEBUG mode disabled (`DEBUG=false`)
- [ ] Secrets in environment variables (not hardcoded)
- [ ] `.env` excluded from Git (`.gitignore`)
- [ ] Dependency scan clean (`pip-audit`, `npm audit`)
- [ ] Docker images based on official sources
- [ ] Health check endpoint returns minimal info (no stack traces)
- [ ] Rate limiting enabled (if public deployment)

### Post-Deployment

- [ ] Health check accessible: `curl https://<domain>/api/health`
- [ ] SSL certificate valid (check with `ssllabs.com/ssltest`)
- [ ] CORS working (frontend can fetch from backend)
- [ ] Error responses do not leak internal paths
- [ ] Logs do not contain secrets

### Ongoing Maintenance

- [ ] Monthly: Run `pip-audit` and `npm audit`
- [ ] Quarterly: Update dependencies (test first)
- [ ] Annually: Review this SECURITY.md for new threats

---

## Reporting Security Issues

### How to Report

**Do NOT** open a public GitHub Issue for security vulnerabilities.

**Instead:**
1. Email: [security contact email]
2. Subject: "Security Issue: UK Wind Dashboard"
3. Include:
   - Vulnerability description
   - Steps to reproduce
   - Impact assessment
   - Suggested fix (if known)

**Expected Response Time:** 48 hours acknowledgment, 7 days for fix (critical issues).

### Disclosure Policy

- Private disclosure preferred (90-day embargo before public disclosure)
- Credit given to reporter (if desired)
- CVE assigned for high/critical vulnerabilities

---

## Future Enhancements

### v1.1
- Rate limiting on API endpoints
- CSP headers on frontend
- Structured logging (JSON format)

### v2.0
- OAuth 2.0 authentication (Google Workspace, Azure AD)
- Role-based access control (admin, analyst, read-only)
- Audit logging (who accessed what, when)
- API key authentication for programmatic access

### v2.1
- Encrypted cache files (AES-256)
- Secret rotation (automated credential refresh)
- WAF integration (Cloudflare, AWS WAF)

---

## Document Version

**Version:** 1.0  
**Last Updated:** 2026-10-26  
**Next Review:** 2026-04-26 (6 months)  
**Owner:** Development Team
