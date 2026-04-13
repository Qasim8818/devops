# Complete Setup Guide

Detailed configuration and deployment instructions.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Prometheus Configuration](#prometheus-configuration)
5. [Slack Integration](#slack-integration)
6. [Ollama/LLM Setup](#ollama-llm-setup)
7. [Security Hardening](#security-hardening)
8. [Performance Tuning](#performance-tuning)
9. [Monitoring Setup](#monitoring-setup)
10. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum
- **CPU**: 2 cores (4+ recommended)
- **RAM**: 4GB (8GB+ recommended)
- **Storage**: 20GB free space
- **OS**: Linux, macOS, or Windows (WSL2)

### Production
- **CPU**: 4+ cores (8+ for high volume)
- **RAM**: 16GB+
- **Storage**: 100GB+ (SSD recommended)
- **Network**: 1Gbps connection

### Software
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (local development)
- Node 18+ (frontend development)

---

## Environment Configuration

### Generate Secret Key
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Set Production .env
```bash
# Security
SECRET_KEY=your-generated-key-here
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# API
FASTAPI_PORT=8000
LOG_LEVEL=WARNING

# Database
DB_URL=postgresql://devsecops:STRONG_PASSWORD@postgres:5432/devsecops

# LLM
OLLAMA_API_URL=http://ollama:11434
LLM_MODEL=llama2
LLM_TIMEOUT=60

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
MONITOR_INTERVAL=60

# Alerting
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-token
ENABLE_SLACK_INTEGRATION=true

# Auto-Remediation
ENABLE_AUTO_REMEDIATION=true
REMEDIATION_TIMEOUT=300
COMMAND_EXECUTION_ALLOWED=true

# Features
ENABLE_CVE_SCANNER=true
ENABLE_PDF_REPORTS=true
ENABLE_COST_ANOMALY_DETECTION=true
```

---

## Database Setup

### Initialize PostgreSQL
```bash
# Run migrations (once inside backend container)
cd /app
alembic upgrade head
```

### Backup Database
```bash
docker compose exec postgres pg_dump -U devsecops devsecops > backup.sql
```

### Restore Database
```bash
docker compose exec -T postgres psql -U devsecops devsecops < backup.sql
```

---

## Prometheus Configuration

### Add Custom Scrape Jobs

Edit `monitoring/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'custom-app'
    static_configs:
      - targets: ['localhost:9100']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+)(?::\d+)?'
        replacement: '${1}'
```

### Create Custom Alert Rules

Edit `monitoring/alert_rules.yml`:

```yaml
- alert: CustomMetricHigh
  expr: custom_metric > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Custom metric exceeded"
```

---

## Slack Integration

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Enter app name: "DevSecOps Agent"
5. Select your workspace

### 2. Generate Bot Token

1. Navigate to "OAuth & Permissions"
2. Add scopes: `chat:write`, `files:write`, `app_mentions:read`
3. Copy Bot Token (starts with `xoxb-`)

### 3. Create Webhook URL

1. Navigate to "Incoming Webhooks"
2. Toggle "On"
3. Click "Add New Webhook to Workspace"
4. Select a channel
5. Copy the webhook URL

### 4. Update .env

```bash
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
SLACK_CHANNEL_ALERTS=#devsecops-alerts
ENABLE_SLACK_INTEGRATION=true
```

---

## Ollama/LLM Setup

### Install Models

```bash
# Inside ollama container
docker compose exec ollama ollama pull llama2

# Or use other models
docker compose exec ollama ollama pull mistral
docker compose exec ollama ollama pull neural-chat
```

### Verify Installation

```bash
curl http://localhost:11434/api/tags
```

### Use Different Model

```bash
# Update .env
LLM_MODEL=mistral
```

---

## Security Hardening

### 1. Network Security

```yaml
# In docker-compose.yml
networks:
  devsecops:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.enable_ip_masquerade: "true"
```

### 2. SSL/TLS

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365

# In production, use Let's Encrypt
```

### 3. Environment Variable Secrets

```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use secure secret management
# Example: AWS Secrets Manager, HashiCorp Vault
```

### 4. Database Security

```bash
# Strong password for PostgreSQL
DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")

# Restrict database access
```

---

## Performance Tuning

### Backend Optimization

```bash
# Increase worker processes
# In docker-compose.yml backend service:
command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Increase connection pool
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=20
```

### Prometheus Data Retention

```yaml
# In docker-compose.yml
command:
  - '--storage.tsdb.retention.time=90d'
  - '--storage.tsdb.max-block-duration=30d'
```

### Database Query Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);
```

---

## Monitoring Setup

### Import Grafana Dashboards

1. Go to http://localhost:3000
2. Login: admin / admin
3. Import dashboard JSON files from `monitoring/grafana/dashboards/`
4. Select Prometheus datasource

### Custom Prometheus Queries

```promql
# CPU Usage
rate(container_cpu_usage_seconds_total[1m]) * 100

# Memory Usage
container_memory_usage_bytes / 1024 / 1024

# Request Rate
rate(http_requests_total[5m])

# Error Rate
rate(http_requests_total{status=~"5.."}[5m])
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port in .env
FASTAPI_PORT=8001
```

### Database Connection Failed

```bash
# Check PostgreSQL health
docker compose ps postgres

# Check logs
docker compose logs postgres

# Restart database
docker compose restart postgres
```

### Ollama Model Won't Load

```bash
# Check available disk space
df -h

# Increase Ollama memory
docker compose exec ollama ollama pull --mem 4gb llama2
```

### High Memory Usage

```bash
# Reduce Prometheus retention
--storage.tsdb.retention.size=10GB

# Clear Docker cache
docker system prune -a

# Disable unused features
ENABLE_CVE_SCANNER=false
```

---

## Health Checks

```bash
# API health
curl http://localhost:8000/health/status

# Database health
docker compose exec postgres pg_isready -U devsecops

# Prometheus health
curl http://localhost:9090/-/healthy

# Grafana health
curl http://localhost:3000/api/health
```

---

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/devsecops"
mkdir -p $BACKUP_DIR

# Backup database
docker compose exec -T postgres pg_dump -U devsecops devsecops | \
  gzip > $BACKUP_DIR/db-$(date +%Y%m%d).sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

---

## Scale to Production

### Kubernetes Deployment

See [K8S.md](K8S.md) for Helm charts and Kubernetes manifests.

### Load Balancing

- Use NGINX reverse proxy
- Configure health checks
- Enable connection pooling
