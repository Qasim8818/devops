# DevSecOps Agent — Pre-Deployment Audit Report
**Date:** 2026-04-28 | **Auditor:** Claude (Anthropic) | **Verdict:** ⚠️ NOT READY — Fix 2 critical bugs first

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 Critical | 2 | Must fix before ANY deploy |
| 🟠 High | 4 | Fix before shipping to client |
| 🟡 Medium | 3 | Fix in this sprint |
| 🔵 Low | 2 | Nice-to-have |

The architecture is solid and the overall code quality is production-grade. The backend, monitoring stack, Docker setup, and frontend are all well-structured. However there are **2 critical bugs that will break the deployment immediately** and **4 high issues that will embarrass you in front of the client**.

---

## 🔴 CRITICAL — Will Break On First Deploy

### BUG-1: Database Password Mismatch (App Will Fail to Start)

**File:** `.env` + `docker-compose.yml`

The PostgreSQL container is started with `${DB_PASSWORD:-changeme}` (defaults to `changeme` since `DB_PASSWORD` is not set in `.env`), but the backend's `DB_URL` in `.env` uses a completely different password:

```
# .env
DB_URL=postgresql://devsecops:SecureDbP@ssw0rd!2024@postgres:5432/devsecops
# docker-compose.yml postgres service
POSTGRES_PASSWORD=${DB_PASSWORD:-changeme}   ← resolves to "changeme"
```

The backend will fail to authenticate to the database on startup. `init_db()` will throw, and the app will crash.

**Fix — add ONE line to `.env`:**
```
DB_PASSWORD=SecureDbP@ssw0rd!2024
```

---

### BUG-2: Ollama LLM Model Never Downloaded (AI Engine Dead on First Boot)

**File:** `docker-compose.yml`

The `ollama` service starts successfully (the container is healthy), but `llama2` model is never pulled inside it. The backend depends on `ollama: condition: service_healthy` and will start, but every AI analysis call will fail. `LLM_FALLBACK_MODE=true` prevents a crash, but the core selling feature (AI root cause analysis) silently doesn't work.

**Fix — add a model-pull init container to `docker-compose.yml`:**
```yaml
  ollama-init:
    image: ollama/ollama:latest
    container_name: ollama-init
    depends_on:
      ollama:
        condition: service_healthy
    entrypoint: ["ollama", "pull", "llama2"]
    environment:
      - OLLAMA_HOST=http://ollama:11434
    networks:
      - devsecops
    restart: "no"
```

Or add a one-time manual step to the deploy docs:
```bash
docker exec ollama ollama pull llama2
```

---

## 🟠 HIGH — Fix Before Client Delivery

### HIGH-1: `health` Module Import Shadowed in `main.py`

**File:** `backend/main.py` line 55

```python
from routes import api, health, incidents, audit, remediation   # health = router module

# Inside lifespan():
health = await app_state["ai_engine"].health_check()  # ← OVERWRITES the import
if not health["status"] == "healthy":
    ...

# Line 94 (module level — runs before lifespan, so works TODAY):
app.include_router(health.router, prefix="/health", ...)  # ← would break if order changes
```

This works right now only because `app.include_router()` runs at module load before `lifespan()`. It's a landmine — any refactor could break it silently.

**Fix:**
```python
ai_health = await app_state["ai_engine"].health_check()
if not ai_health["status"] == "healthy":
    logger.warning(f"AI Engine health: {ai_health}")
```

---

### HIGH-2: Grafana Admin Password Is `admin` in Production Docker Compose

**File:** `docker-compose.yml` line 32

```yaml
- GF_SECURITY_ADMIN_PASSWORD=admin
```

This is shipped as-is to the client. Any exposed port 3000 is instantly compromised.

**Fix — use `.env`:**
```yaml
# docker-compose.yml
- GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}

# .env
GRAFANA_ADMIN_PASSWORD=<generate-strong-password>
```

---

### HIGH-3: Hardcoded `localhost` Links in Production Frontend

**File:** `frontend/src/Dashboard.jsx` lines 418, 424

```jsx
href="http://localhost:3000"      // Grafana link — broken on any real server
href="http://localhost:8000/docs" // API docs link — broken on any real server
```

When the client deploys this on a VPS/cloud, every link in the dashboard that says "Open Grafana" or "API Docs" will 404.

**Fix:**
```jsx
const grafanaUrl = process.env.REACT_APP_GRAFANA_URL || 'http://localhost:3000';
const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Then use:
href={grafanaUrl}
href={`${apiUrl}/docs`}
```

Add to `docker-compose.yml` frontend environment:
```yaml
- REACT_APP_GRAFANA_URL=http://your-server:3000
- REACT_APP_API_URL=http://your-server:8000
```

---

### HIGH-4: `CVEScanner` Imported But Never Used in `api.py`

**File:** `backend/routes/api.py` line 11

```python
from advanced.cve_scanner import CVEScanner   # imported but zero routes use it
```

This is either a dead import (remove it) or a missing feature (add routes for it). Client paid for CVE scanning, so clarify this.

**Fix option A** — remove if not in scope:
```python
# Delete line 11
```

**Fix option B** — add the routes (takes ~30 min):
```python
@router.get("/cve/scan-image")
async def scan_image(image: str):
    scanner = CVEScanner()
    return await scanner.scan_docker_image(image)

@router.get("/cve/latest")
async def latest_cves(hours: int = 24):
    scanner = CVEScanner()
    return await scanner.get_latest_cves(hours)
```

---

## 🟡 MEDIUM — Fix This Sprint

### MED-1: Duplicate Key in `.env`

**File:** `.env`

`ENABLE_SLACK_INTEGRATION` is defined twice (both `false`). Pydantic-settings uses the last value, so it's not broken, but it's unprofessional and will confuse whoever manages the deployment.

**Fix:** Remove the duplicate. Keep only one:
```
ENABLE_SLACK_INTEGRATION=false
```

---

### MED-2: Monitoring Anomaly Timestamps Never Set — Time Filter Always Broken

**File:** `backend/core/monitoring.py` line 175

`get_recent_anomalies()` filters by `detected_at`:
```python
return [a for a in self.anomalies if a.get("detected_at", datetime.utcnow()) > cutoff]
```

But `_analyze_metrics()` never sets `detected_at` on any anomaly dict. So the fallback `datetime.utcnow()` is always used, which is always greater than the cutoff — meaning **all** anomalies are always returned, the filter never actually filters anything.

**Fix — add timestamp when building anomaly dicts in `_analyze_metrics()`:**
```python
anomalies.append({
    "metric": "container_cpu",
    ...
    "detected_at": datetime.utcnow(),   # ← add this line to every append()
})
```

---

### MED-3: Audit Report Endpoints Are Hardcoded Stubs

**File:** `backend/routes/audit.py`

`/api/audit/generate` returns a hardcoded `report_id: "audit_20260413_001"` from April 2026. The status endpoint always returns `"completed"` with hardcoded findings counts. These aren't connected to real data.

The PDF download (`/api/audit/{report_id}/pdf`) works correctly and generates a real PDF. But the report ID plumbing is broken.

**Minimum fix before ship:**
```python
import uuid

@router.get("/generate")
async def generate_audit_report():
    report_id = f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    return {
        "report_id": report_id,
        "status": "generating",
        ...
    }
```

---

## 🔵 LOW — Recommended Improvements

### LOW-1: Dockerfile.backend Has No HEALTHCHECK

Docker Compose defines the healthcheck, so this won't break anything. But the image itself has no `HEALTHCHECK` directive — if it's ever run without Compose, there's no health signaling.

**Fix:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health/status || exit 1
```

### LOW-2: Frontend Dockerfile Uses Anonymous Stage `--from=0`

**File:** `frontend/Dockerfile`

```dockerfile
COPY --from=0 /app/build ./build   # ← unclear
```

**Fix:**
```dockerfile
FROM node:18-alpine AS build
...
FROM node:18-alpine
COPY --from=build /app/build ./build   # ← clear
```

---

## What IS Working Correctly ✅

- **FastAPI app structure** — clean, async, lifespan management correct
- **SQLAlchemy async setup** — `asyncpg` driver, `AsyncSession`, dependency injection all correct
- **All 5 route modules** — incidents, remediation, health, audit, api — logic is clean and properly uses DB sessions
- **MonitoringEngine** — async loop, Prometheus queries, anomaly detection logic all correct
- **AIEngine** — Ollama integration with proper fallback to rule-based analysis
- **AlertingEngine** — Slack, email, webhook channels properly structured
- **PDFReportGenerator** — fully working ReportLab implementation, generates real PDFs
- **Docker Compose** — all services (Prometheus, Grafana, Loki, Promtail, Ollama, Postgres, Backend, Frontend) with healthchecks and proper `depends_on`
- **Frontend Dashboard** — React + Tailwind + Recharts, polls API every 30s, graceful error handling
- **`requirements.txt`** — all dependencies present including `asyncpg`
- **`.env` SECRET_KEY** — properly generated (not default)
- **`config.py`** — pydantic-settings, all env vars typed, `lru_cache` for settings
- **Prometheus/Grafana/Loki configs** — all present and valid
- **Security defaults** — `COMMAND_EXECUTION_ALLOWED=false`, `SAFE_COMMANDS_ONLY=true`

---

## Pre-Deploy Checklist

```
[ ] Add DB_PASSWORD=SecureDbP@ssw0rd!2024 to .env            ← CRITICAL BUG-1
[ ] Add ollama model pull step to startup docs or compose     ← CRITICAL BUG-2
[ ] Rename 'health' variable in main.py lifespan             ← HIGH-1
[ ] Set GRAFANA_ADMIN_PASSWORD in .env                       ← HIGH-2
[ ] Fix localhost hardcodes in Dashboard.jsx                 ← HIGH-3
[ ] Remove/implement CVEScanner import in api.py             ← HIGH-4
[ ] Remove duplicate ENABLE_SLACK_INTEGRATION from .env      ← MED-1
[ ] Add detected_at to anomaly dicts in monitoring.py        ← MED-2
[ ] Fix hardcoded report_id in audit.py                      ← MED-3
[ ] docker-compose down -v && docker-compose build --no-cache && docker-compose up -d
[ ] curl -f http://localhost:8000/health/status → {"status": "healthy"}
[ ] curl http://localhost:8000/api/status → features listed
[ ] Open http://localhost:3001 → Dashboard loads, no console errors
```

---

## Deploy Command (After All Fixes Applied)

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
docker exec ollama ollama pull llama2     # one-time model download (~4GB)
docker-compose ps                         # verify all 8 services healthy
curl -f http://localhost:8000/health/status
```

---

*Report generated by Claude (Anthropic) — 2026-04-28*
