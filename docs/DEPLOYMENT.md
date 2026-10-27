# Deployment Guide

## Prerequisites

### Local Development
- Node.js 22+ and npm 10+
- Python 3.12+
- Docker 24+ and Docker Compose 2+
- Git

### Production
- Docker-compatible hosting (Railway, Render, AWS ECS, Azure Container Apps)
- Domain with SSL/TLS certificate (recommended)
- Environment variables configuration

---

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd uk-energy-analytics-dashboard
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Create `.env` file:**
```bash
ELEXON_BASE_URL=https://data.elexon.co.uk/bmrs/api/v1
FORECAST_CUTOFF_HOUR=9
ANALYSIS_YEAR=2026
ANALYSIS_MONTH=1
CACHE_DIR=./cache
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Run backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:** http://localhost:8000/api/health

### 3. Frontend Setup
```bash
cd frontend
npm install
```

**Create `.env` file:**
```bash
VITE_API_URL=http://localhost:8000
```

**Run frontend:**
```bash
npm run dev
```

**Access:** http://localhost:5173

---

## Docker Deployment

### Build and Run Locally
```bash
# From project root
docker compose build
docker compose up
```

**Services:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

**Verify:**
```bash
curl http://localhost:8000/api/health
curl http://localhost:3000
```

### Docker Compose Configuration
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ELEXON_BASE_URL=https://data.elexon.co.uk/bmrs/api/v1
      - FORECAST_CUTOFF_HOUR=9
      - CACHE_DIR=/app/cache
    volumes:
      - cache-data:/app/cache
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://backend:8000
    depends_on:
      - backend

volumes:
  cache-data:
```

---

## Production Deployment

### Option 1: Railway (Recommended)

**Backend:**
1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Create project: `railway init`
4. Deploy backend:
   ```bash
   cd backend
   railway up
   ```
5. Set environment variables in Railway dashboard:
   - `ELEXON_BASE_URL=https://data.elexon.co.uk/bmrs/api/v1`
   - `FORECAST_CUTOFF_HOUR=9`
   - `CORS_ORIGINS=https://<frontend-domain>`
6. Provision persistent volume at `/app/cache` (Railway volumes)

**Frontend:**
1. Create separate Railway service for frontend
2. Set build command: `npm run build`
3. Set start command: `npx serve -s dist -l 80`
4. Set environment variable: `VITE_API_URL=https://<backend-domain>`
5. Deploy: `railway up`

### Option 2: Vercel (Frontend) + Render (Backend)

**Backend on Render:**
1. Connect GitHub repository
2. Create new Web Service
3. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment: Docker or Python 3.12
4. Add environment variables
5. Add persistent disk at `/app/cache` (Render Disks)

**Frontend on Vercel:**
1. Import project from Git
2. Framework: Vite
   - Set the project Root Directory to `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. The checked-in `frontend/vercel.json` rewrites `/api/*` requests to the deployed backend, so a `VITE_API_URL` setting is not needed for this setup. Update its destination if the backend domain changes.
6. Confirm `https://<backend-domain>/api/health` returns HTTP 200 after deploying the backend.

### Option 3: AWS (ECS + Fargate)

**Prerequisites:**
- AWS CLI configured
- ECR repositories created
- ECS cluster created

**Build and push images:**
```bash
# Backend
cd backend
docker build -t uk-energy-backend .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag uk-energy-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/uk-energy-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/uk-energy-backend:latest

# Frontend
cd frontend
docker build -t uk-energy-frontend .
docker tag uk-energy-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/uk-energy-frontend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/uk-energy-frontend:latest
```

**ECS Task Definition:**
- Backend: 512 CPU, 1024 MB memory, port 8000
- Frontend: 256 CPU, 512 MB memory, port 80
- Persistent storage: EFS volume mounted at `/app/cache`

**Load Balancer:**
- Application Load Balancer with SSL/TLS certificate
- Backend target group: port 8000, path `/api/health`
- Frontend target group: port 80, path `/`

---

## Environment Variables

### Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ELEXON_BASE_URL` | Yes | - | Elexon BMRS API base URL |
| `FORECAST_CUTOFF_HOUR` | No | 9 | Hour (0-23) for D-1 cutoff |
| `ANALYSIS_YEAR` | No | 2026 | Year for data analysis |
| `ANALYSIS_MONTH` | No | 1 | Month (1-12) for analysis |
| `CACHE_DIR` | No | `./cache` | Cache directory path |
| `CORS_ORIGINS` | Yes | - | Comma-separated allowed origins |
| `HTTPX_TIMEOUT` | No | 30.0 | API request timeout (seconds) |
| `PORT` | No | 8000 | Server port |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | Yes | - | Backend API base URL |

---

## Cache Strategy

### First Startup
Backend fetches all January 2026 data from Elexon API (~30 API calls, 2-3 minutes). Cache files written to `CACHE_DIR`.

### Subsequent Startups
Backend loads from disk cache. Zero API calls. Startup time <5 seconds.

### Cache Invalidation
Delete cache directory to force re-fetch:
```bash
rm -rf backend/cache/*
```

### Production Cache Volume
**Critical:** Mount persistent volume at `/app/cache` to preserve cache across container restarts.

**Railway:**
```bash
railway volume create cache-volume
railway volume attach cache-volume /app/cache
```

**Render:**
Add Disk in service settings, mount path: `/app/cache`

**AWS ECS:**
Use EFS file system, mount at `/app/cache` in task definition.

---

## Health Checks

### Backend Health Endpoint
```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{
  "status": "ok",
  "cache_loaded": true,
  "dates_cached": 31,
  "total_pairs": 744
}
```

**Status codes:**
- `200` — Healthy, cache loaded
- `503` — Unhealthy, cache not loaded (first startup)

### Frontend Health Check
```bash
curl -I http://localhost:3000
```

**Expected:** `200 OK`

---

## SSL/TLS Configuration

### Railway / Render / Vercel
Automatic SSL via platform (Let's Encrypt).

### AWS ALB
1. Request certificate in ACM
2. Attach to ALB listener (port 443)
3. Redirect HTTP → HTTPS:
   ```
   Listener: HTTP:80 → Redirect to HTTPS:443
   ```

### Nginx (self-hosted)
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Monitoring

### Backend Metrics
- `/api/health` — Cache status, completeness
- `/api/metadata` — Data source info
- Uvicorn logs: stdout/stderr

### Frontend Metrics
- Nginx access logs (if using nginx)
- Browser DevTools Network tab
- Core Web Vitals (LCP, CLS, FID)

### Recommended Tools
- Uptime monitoring: UptimeRobot, Pingdom
- Error tracking: Sentry
- Application monitoring: New Relic, Datadog

---

## Rollback Procedure

### Railway / Render
Use platform dashboard to rollback to previous deployment.

### Docker Compose
```bash
# Rebuild from previous commit
git checkout <previous-commit>
docker compose down
docker compose build
docker compose up -d
```

### ECS
Update service to use previous task definition revision.

---

## Troubleshooting

### Backend won't start
**Symptom:** `500 Internal Server Error` on all endpoints  
**Cause:** Missing environment variables or cache directory  
**Fix:**
```bash
export ELEXON_BASE_URL=https://data.elexon.co.uk/bmrs/api/v1
export CORS_ORIGINS=http://localhost:5173
mkdir -p cache
```

### Frontend shows "Network Error"
**Symptom:** All API calls fail with CORS error  
**Cause:** Backend CORS_ORIGINS doesn't include frontend domain  
**Fix:** Add frontend URL to `CORS_ORIGINS`

### Cache not persisting across restarts
**Symptom:** Backend re-fetches data every startup  
**Cause:** No persistent volume mounted  
**Fix:** Mount volume at `/app/cache` (see Cache Strategy section)

### Slow initial load
**Symptom:** Dashboard takes 2-3 minutes to load on first startup  
**Cause:** Cache warming in progress  
**Fix:** This is expected. Subsequent loads are instant. Pre-warm cache before deployment:
```bash
python -c "import asyncio; from app.services.cache_manager import cache_manager; asyncio.run(cache_manager.warm_cache())"
```

### 404 on frontend routes
**Symptom:** Refresh on `/accuracy` returns 404  
**Cause:** Nginx/server not configured for SPA  
**Fix:** Add fallback to `index.html` (see nginx.conf in frontend/)

---

## Security Checklist

- ✅ HTTPS/SSL enabled in production
- ✅ CORS configured with specific origins (not `*`)
- ✅ No secrets in code or Docker images
- ✅ Environment variables set via platform (not hardcoded)
- ✅ Docker images built from official base images
- ✅ Dependencies regularly updated (`npm audit`, `pip-audit`)
- ✅ Health check endpoints return minimal information (no internal errors)
- ✅ Rate limiting on backend (optional, not implemented — Elexon API has no limits)

---

## Performance Optimization

### Backend
- Cache all January 2026 data in memory (744 pairs)
- No database queries (in-memory only)
- Async HTTPX for parallel Elexon API calls
- Gzip compression enabled (FastAPI default)

### Frontend
- Vite production build with code splitting
- Recharts lazy-loaded via dynamic import
- TanStack Query with `staleTime: Infinity` (historical data)
- Images: WebP format, lazy loading

### Expected Performance
- **TTFB (backend):** <100ms (after cache warm)
- **LCP (frontend):** <2.5s
- **CLS:** <0.1
- **FID:** <100ms

---

## Backup and Recovery

### Data Backup
**What to back up:**
- Cache directory (`/app/cache/*.json`)

**Backup command:**
```bash
tar -czf cache-backup-$(date +%Y%m%d).tar.gz backend/cache/
```

**Restore command:**
```bash
tar -xzf cache-backup-20260126.tar.gz -C backend/
```

### Configuration Backup
- `.env` files (exclude from version control)
- `docker-compose.yml`
- `nginx.conf` (if applicable)

**Store backups in:**
- S3 bucket (encrypted)
- Encrypted git repository (for configs only, not cache data)

---

## Scaling

### Horizontal Scaling
Backend is stateless except for in-memory cache. For multi-instance:

**Option 1:** Shared cache via Redis
- Replace `cache_manager.py` to use Redis
- All instances share same cache

**Option 2:** File-based cache on shared volume
- Mount EFS/NFS at `/app/cache` on all instances
- Instances load from shared disk

**Option 3:** Pre-warmed cache in Docker image
- Run cache warm during Docker build
- Bake cache into image layer
- No runtime API dependency

### Vertical Scaling
**Backend:** 512 MB RAM sufficient for 744 pairs  
**Frontend:** Static assets, no runtime memory

---

## CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      
      - name: Test Frontend
        run: |
          cd frontend
          npm install
          npm run build
      
      - name: Deploy to Railway
        run: |
          npm i -g @railway/cli
          railway up --service backend
          railway up --service frontend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## Post-Deployment Validation

1. **Health check:** `curl https://<domain>/api/health` → 200 OK
2. **Dashboard loads:** Visit `https://<domain>` → KPI grid renders
3. **Data completeness:** Check dashboard shows "744/744 hours (100%)"
4. **Time series chart:** Navigate to Time Series page → chart renders
5. **API responses:** Check browser DevTools Network tab → no 500 errors
6. **Cache persistence:** Restart backend → health check still shows `cache_loaded: true`

---

## Support and Maintenance

### Logs Access
**Railway:** `railway logs --service backend`  
**Render:** View in dashboard  
**AWS:** CloudWatch Logs

### Updates
**Dependencies:**
```bash
# Backend
cd backend && pip list --outdated
pip install -U <package>

# Frontend
cd frontend && npm outdated
npm update
```

**Elexon API changes:**
Monitor https://bmrs.elexon.co.uk/api-documentation for breaking changes.

---

## Contact and Escalation

For deployment issues:
1. Check logs for error messages
2. Verify environment variables are set
3. Confirm persistent volume mounted at `/app/cache`
4. Review CORS origins configuration
5. Test health endpoint directly

**Common gotchas:**
- CORS origin mismatch (frontend domain not in backend `CORS_ORIGINS`)
- Missing persistent volume (cache re-fetches every restart)
- Wrong `VITE_API_URL` (frontend can't reach backend)
