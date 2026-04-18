# DevSecOps Agent - Fix 3
## SECRET_KEY Generation & Complete .env Configuration

**Date**: April 18, 2026  
**Severity**: CRITICAL - Default SECRET_KEY is insecure and must be changed

---

## Problem Statement

The default SECRET_KEY ("change-me-in-production") is:

- Not cryptographically secure
- Known to all users
- Violates production security requirements

Additionally, the `.env` file must be completely and correctly configured for all features to work properly.

---

## Solution: Step-by-Step

### Step 1: Generate a Strong SECRET_KEY

Run this command to generate a 32-character cryptographically secure key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output**:
```
kJ7xPq9Zx_ABC123DEF456GHI789JKL-uvwxyz
```

Copy this exact value - you'll need it for Step 2.

---

### Step 2: Create Complete Production .env File

Create or update `.env` in your project root with this complete content:

```
# ============================================================================
# DevSecOps Agent - Complete Environment Configuration
# Production Grade - Change all default values before deploying
# ============================================================================

# ============ SECURITY (CRITICAL) ============
# REQUIRED: Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=paste-your-generated-key-from-step-1-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# ============ DATABASE ============
# PostgreSQL connection string - must match docker-compose postgres service
DB_URL=postgresql://devsecops:changeme@postgres:5432/devsecops
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# ============ API CONFIGURATION ============
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# ============ AI/LLM ENGINE ============
OLLAMA_API_URL=http://ollama:11434
LLM_MODEL=llama2
LLM_TIMEOUT=30
LLM_FALLBACK_MODE=true

# ============ MONITORING STACK ============
PROMETHEUS_URL=http://prometheus:9090
PROMETHEUS_SCRAPE_INTERVAL=15
LOKI_URL=http://loki:3100

# ============ SLACK INTEGRATION (OPTIONAL) ============
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_CHANNEL_ALERTS=#devsecops-alerts
ENABLE_SLACK_INTEGRATION=false

# ============ EMAIL ALERTING (OPTIONAL) ============
ALERT_EMAIL_ENABLED=false
ALERT_EMAIL_FROM=alerts@devsecops.local
ALERT_EMAIL_SMTP_HOST=localhost
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_PASSWORD=your_app_password

# ============ WEBHOOK CONFIGURATION ============
WEBHOOK_ENABLED=true
WEBHOOK_TIMEOUT=10

# ============ MONITORING INTERVALS ============
MONITOR_INTERVAL=30
HEALTH_CHECK_INTERVAL=60
INCIDENT_RETENTION_DAYS=30

# ============ AUTO-REMEDIATION ============
ENABLE_AUTO_REMEDIATION=true
REMEDIATION_TIMEOUT=300
REMEDIATION_RETRY_COUNT=3

# ============ FEATURE FLAGS ============
ENABLE_SLACK_INTEGRATION=false
ENABLE_CVE_SCANNER=false
ENABLE_COST_ANOMALY_DETECTION=false
ENABLE_PDF_REPORTS=true

# ============ SECURITY SETTINGS ============
COMMAND_EXECUTION_ALLOWED=false
SAFE_COMMANDS_ONLY=true

# ============ AI MODEL THRESHOLDS ============
ANOMALY_SCORE_THRESHOLD=0.7
CONFIDENCE_THRESHOLD=0.8
```

**IMPORTANT**: Replace `paste-your-generated-key-from-step-1-here` with the actual key generated in Step 1.

---

### Step 3: Set Proper File Permissions

The `.env` file contains sensitive data and should have restricted permissions:

```bash
# Set permissions so only owner can read/write
chmod 600 .env

# Verify permissions (should show: -rw-------)
ls -la .env
```

---

### Step 4: Ensure .env is in .gitignore

Never commit `.env` to version control:

```bash
# Add .env to .gitignore if not already present
echo ".env" >> .gitignore

# Verify it was added
cat .gitignore | grep .env
```

---

## Complete Deployment Sequence

### Phase 1: Configuration & Setup (5 minutes)

1. **Generate SECRET_KEY using command from Step 1**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Create `.env` file in project root with content from Step 2**
   ```bash
   # Copy the complete .env content from Step 2 into your .env file
   nano .env  # or your preferred editor
   ```

3. **Replace the placeholder with your generated key**
   - Find: `paste-your-generated-key-from-step-1-here`
   - Replace with: Your actual generated key from Step 1

4. **Set file permissions**
   ```bash
   chmod 600 .env
   ```

5. **Update .gitignore**
   ```bash
   echo ".env" >> .gitignore
   ```

### Phase 2: Start Services (2-3 minutes)

```bash
# Start all containers
docker-compose up -d

# Wait 30-60 seconds for all services to start
sleep 30

# Verify all containers are running
docker-compose ps
```

### Phase 3: Health Checks (2 minutes)

**API Health**:
```bash
curl http://localhost:8000/health/status
```

Expected response:
```json
{
  "status": "operational",
  "version": "1.0.0",
  "timestamp": "2026-04-18T21:00:00Z"
}
```

**List Incidents** (should be empty):
```bash
curl http://localhost:8000/api/incidents
```

Expected: `[]`

**System Configuration**:
```bash
curl http://localhost:8000/api/config
```

**Check All Containers**:
```bash
docker-compose ps
```

All containers should show `Up` status and healthy.

### Phase 4: Smoke Testing (3 minutes)

| Test | Command | Expected Result |
|------|---------|-----------------|
| API Health | `curl http://localhost:8000/health/status` | 200 OK with JSON |
| List Incidents | `curl http://localhost:8000/api/incidents` | `[]` (empty) |
| System Config | `curl http://localhost:8000/api/config` | 200 OK with config |
| List Rules | `curl http://localhost:8000/api/remediation/rules` | `[]` (empty) |
| Containers | `docker-compose ps` | All `Up` and healthy |

---

## Production Hardening Checklist

Before deploying to production, verify all of these:

✅ SECRET_KEY is unique (generated, not default)  
✅ .env file has 600 permissions (`-rw-------`)  
✅ .env is in .gitignore and never committed to git  
✅ DEBUG=false in production .env  
✅ ALLOWED_HOSTS set to actual production domain(s)  
✅ Database password changed from "changeme" to strong password  
✅ SLACK credentials (if used) are from your Slack workspace  
✅ COMMAND_EXECUTION_ALLOWED=false unless explicitly needed  
✅ All containers pass health checks  
✅ API endpoints responding correctly  

---

## Advanced Configuration Options

### For Slack Integration

1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Create bot token: https://api.slack.com/apps
3. Update .env:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/ACTUAL/WEBHOOK
   SLACK_BOT_TOKEN=xoxb-your-actual-token
   ENABLE_SLACK_INTEGRATION=true
   ```

### For Email Alerting

1. Generate app password from your email provider
2. Update .env:
   ```
   ALERT_EMAIL_ENABLED=true
   ALERT_EMAIL_SMTP_HOST=smtp.gmail.com  # or your provider
   ALERT_EMAIL_PASSWORD=your-app-password
   ```

### For Custom Domain

Update .env:
```
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
```

---

## Troubleshooting

### "Secret key is not secure" error

**Cause**: Using default or weak SECRET_KEY  
**Solution**: 
```bash
# Regenerate using:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with new key
# Restart: docker-compose restart backend
```

### Environment variables not loaded

**Cause**: .env file not in correct location  
**Solution**:
- Verify .env exists in project root: `ls -la .env`
- Check it's not in a subdirectory
- Verify file encoding is UTF-8

### API returns 500 errors

**Cause**: Configuration issues  
**Solution**:
```bash
# Check backend logs for specific error
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Check health status
curl http://localhost:8000/health/status
```

### Database connection fails

**Cause**: DB_URL misconfigured  
**Solution**:
1. Verify postgres container is running: `docker-compose ps postgres`
2. Check DB_URL format: `postgresql://user:pass@postgres:5432/devsecops`
3. Ensure "postgres" is used as hostname (not localhost)

### Containers not starting

**Cause**: Port conflicts or resource issues  
**Solution**:
```bash
# Check what's using ports
lsof -i :8000   # FastAPI
lsof -i :5432   # PostgreSQL
lsof -i :9090   # Prometheus

# Stop conflicting services and retry:
docker-compose down
docker-compose up -d
```

---

## Next Steps After Deployment

1. ✅ Complete all three fixes (Database, Routes, Security)
2. ✅ Run full smoke test suite
3. ✅ Set up monitoring dashboards in Grafana
4. ✅ Configure Slack integration for alerts
5. ✅ Test incident detection and auto-remediation
6. ✅ Configure backups for PostgreSQL
7. ✅ Set up log rotation for Loki
8. ✅ Document custom remediation rules

---

## Security Best Practices

1. **Rotate secrets regularly**: Every 90 days minimum
2. **Use strong passwords**: Minimum 16 characters with special chars
3. **Enable HTTPS**: Required for production
4. **Restrict ALLOWED_HOSTS**: Never use `*` in production
5. **Audit logs**: Monitor who accesses the system
6. **Backup database**: Daily backups with encryption
7. **Keep dependencies updated**: Regular security patches

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **Project Docs**: See README.md in project root
- **Monitoring**: http://localhost:3000 (Grafana)
- **Logs**: `docker-compose logs [service-name]`
