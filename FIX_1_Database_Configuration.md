# DevSecOps Agent - Fix 1
## Database Configuration & DB_URL Conflict Resolution

**Date**: April 18, 2026  
**Project**: DevSecOps Agent - Self-Healing Infrastructure Monitoring  
**Severity**: HIGH - Database connectivity required for all operations

---

## Problem Statement

The application requires a valid PostgreSQL database connection string (DB_URL) to be configured in the `.env` file. Without proper configuration, the system cannot:

- Initialize database tables
- Store incident records
- Persist remediation history
- Track audit logs

This fix ensures the DB_URL is properly configured and conflicts are resolved.

---

## Root Cause

The `.env` file is missing or incomplete. The application has a default DB_URL in `config.py` (`postgresql://devsecops:changeme@postgres:5432/devsecops`) which may conflict with environment-specific configurations needed for your deployment.

---

## Solution

### Step 1: Create .env File

If no `.env` file exists, create one in the project root:

```
DB_URL=postgresql://devsecops:changeme@postgres:5432/devsecops
OLLAMA_API_URL=http://ollama:11434
DEBUG=false
SECRET_KEY=change-me-in-production
ALLOWED_HOSTS=*
LOG_LEVEL=INFO
```

### Step 2: Critical Configuration Parameters

| Parameter | Details |
|-----------|---------|
| **DB_URL** | Must use "postgres" as hostname (Docker DNS). Format: `postgresql://user:pass@host:port/db` |
| **OLLAMA_API_URL** | Must be `http://ollama:11434` in Docker. Use `localhost:11434` for local development. |
| **DEBUG** | Must be `"false"` in production. Only `"true"` during development. |
| **SECRET_KEY** | MUST be changed from default. Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |

### Step 3: Start Database Services

Start PostgreSQL, Prometheus, Loki, and Ollama:

```bash
docker-compose up -d postgres prometheus loki ollama
```

Wait 30-60 seconds for all services to start.

### Step 4: Verify Database Connection

**Check container health**:
```bash
docker-compose ps
```

**View PostgreSQL logs**:
```bash
docker-compose logs postgres
```

**Test DB connection**:
```bash
docker-compose exec postgres psql -U devsecops -d devsecops -c "SELECT version();"
```

**Check tables created**:
```bash
docker-compose exec postgres psql -U devsecops -d devsecops -c "\dt"
```

### Step 5: Start Backend API

Once database is ready, start the backend:

```bash
docker-compose up -d backend
```

---

## Verification Checklist

- ✅ PostgreSQL container is running and healthy
- ✅ Database tables are created: `docker-compose logs backend | grep "Database initialized"`
- ✅ API is accessible: `curl http://localhost:8000/health/status`
- ✅ Incidents endpoint returns empty list: `curl http://localhost:8000/api/incidents`
- ✅ No connection errors in `docker-compose logs backend`

---

## Troubleshooting

### Connection refused error
**Solution**: Ensure postgres service is healthy. Wait 30-60 seconds and check:
```bash
docker-compose logs postgres
```

### DB_URL not recognized
**Solution**: Verify `.env` file is in project root, not in subdirectory. Check file encoding (should be UTF-8).

### Authentication failed
**Solution**: Check `POSTGRES_USER` and `POSTGRES_PASSWORD` in `docker-compose.yml` match DB_URL credentials.

### Tables not created
**Solution**: Backend creates tables automatically. Check `docker-compose logs backend` for errors.

### Port already in use
**Solution**: If port 5432 is in use, change in `docker-compose.yml` to available port.

---

## Next Steps

After fixing database configuration, proceed to:
1. **Fix 2**: SQLAlchemy Async Routes implementation
2. **Fix 3**: SECRET_KEY generation and complete .env setup
3. Full deployment and production hardening
