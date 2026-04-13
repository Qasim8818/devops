# Deployment Guide

Deploy DevSecOps Agent to production.

## Deployment Options

### 1. Docker Compose (Small Deployments)
Suitable for: Single server, < 100K incidents/month

```bash
# Production deployment
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. Kubernetes (Enterprise)
Suitable for: High availability, auto-scaling, multi-region

See [K8S_DEPLOYMENT.md](K8S_DEPLOYMENT.md)

### 3. Cloud Platforms

#### AWS
- ECS with Fargate
- RDS for PostgreSQL
- CloudWatch for monitoring
- See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

#### GCP
- Cloud Run
- Cloud SQL
- Stackdriver
- See [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)

#### Azure
- App Service
- Azure Database
- Application Insights
- See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)

---

## Pre-Deployment Checklist

- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY
- [ ] Review security settings (.env)
- [ ] Set up monitoring/alerting
- [ ] Configure backups
- [ ] Plan rollback strategy
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team trained on operations

---

## Production Configuration

### 1. Environment Variables
Create `.env.production`:

```bash
# Security
DEBUG=false
SECRET_KEY=<generated-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_URL=postgresql://user:STRONG_PASS@db.internal:5432/prod
DB_POOL_SIZE=50

# Logging
LOG_LEVEL=WARNING

# Features
ENABLE_AUTO_REMEDIATION=true
COMMAND_EXECUTION_ALLOWED=true

# Timeouts (production should be higher)
LLM_TIMEOUT=60
REMEDIATION_TIMEOUT=600
```

### 2. Update Docker Compose

```yaml
backend:
  environment:
    - PYTHONUNBUFFERED=1
    - WORKERS=4
  restart: always
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '1'
        memory: 2G
      reservations:
        cpus: '0.5'
        memory: 1G
```

### 3. SSL/TLS Setup

```bash
# Generate certificate (Let's Encrypt)
certbot certonly --standalone -d yourdomain.com

# Update nginx reverse proxy
```

---

## Database Migrations

### First Deployment

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Verify schema
docker compose exec postgres psql -U devsecops -c \
  "SELECT tablename FROM pg_tables WHERE schemaname='public';"
```

### Rolling Updates

```bash
# Back up database
docker compose exec -T postgres pg_dump -U devsecops devsecops | \
  gzip > backup-$(date +%Y%m%d).sql.gz

# Run migrations
docker compose exec backend alembic upgrade head

# On failure, restore from backup
```

---

## Monitoring & Alerts

### Set Up Grafana Alerts

1. Create notification channel
2. Configure alert rules
3. Test alert delivery

### Key Metrics to Monitor

```promql
# System Health
up{job="backend"}

# API Response Time (p99)
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Error Rate
rate(http_requests_total{status=~"5.."}[5m])

# Database Connections
pg_stat_activity_count

# Disk Usage %
(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100
```

### Create Alerting Rules

```yaml
groups:
  - name: production
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 5
        for: 5m
        annotations:
          severity: critical
          
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 1m
        annotations:
          severity: warning
```

---

## Backup Strategy

### Automated Daily Backups

```bash
#!/bin/bash
# /scripts/backup.sh

BACKUP_DIR="/mnt/backups/devsecops"
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# Database backup
docker compose exec -T postgres pg_dump -U devsecops devsecops | \
  gzip > $BACKUP_DIR/db-$(date +%Y%m%d).sql.gz

# Prometheus data
tar czf $BACKUP_DIR/prometheus-$(date +%Y%m%d).tar.gz /prometheus_data

# Clean old backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
```

### Automated Restore Test

```bash
# Weekly restore test to verify backups work
docker compose exec -T postgres psql -U devsecops -c "DROP DATABASE test_restore;"
docker compose exec -T postgres psql -U devsecops -c "CREATE DATABASE test_restore;"
gunzip < backup.sql.gz | docker compose exec -T postgres psql -U devsecops test_restore
```

---

## Scaling Strategy

### Horizontal Scaling (Add Servers)

```yaml
# docker-compose.prod.yml
backend:
  deploy:
    replicas: 3  # Increase this

# Add load balancer
frontend:
  deploy:
    replicas: 2
```

### Vertical Scaling (Bigger Server)

Increase CPU/RAM per service:

```yaml
resources:
  limits:
    cpus: '2'
    memory: 4G
```

### Database Optimization

```sql
-- Create indexes for slow queries
CREATE INDEX idx_incidents_status_created ON incidents(status, created_at);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);

-- Analyze query plans
EXPLAIN ANALYZE SELECT * FROM incidents WHERE status = 'detected';

-- Large table partitioning
CREATE TABLE incidents_2024_q1 PARTITION OF incidents
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

---

## Rollback Plan

### If Deployment Fails

```bash
# Option 1: Revert to previous version
git revert <commit-hash>
docker compose build backend
docker compose up -d backend

# Option 2: Use previous Docker image
docker compose build --build-arg BASE_IMAGE=devsecops:1.0.1 backend
docker compose up -d backend
```

### If Database Migration Fails

```bash
# View migration history
docker compose exec backend alembic history

# Downgrade to previous version
docker compose exec backend alembic downgrade -1

# Restore from backup if needed
```

---

## Production Checklist (Daily)

- [ ] Monitor error rates (< 0.1%)
- [ ] Check database performance
- [ ] Verify backup completion
- [ ] Monitor disk space
- [ ] Check SSL certificate expiry
- [ ] Review recent incidents

---

## Production Checklist (Weekly)

- [ ] Test backup restore
- [ ] Review logs for anomalies
- [ ] Update dependencies (if automatic)
- [ ] Performance profiling
- [ ] Security scan results

---

## Incident Response

### Database Down

```bash
# Check status
docker compose ps postgres

# Restart database
docker compose restart postgres

# If corrupted, restore from backup
```

### API Server Crashed

```bash
# Check logs
docker compose logs backend | tail -100

# Restart service
docker compose restart backend

# Scale up if load issue
docker compose up -d --scale backend=4 backend
```

### High Memory Usage

```bash
# Identify memory leak
docker stats

# Restart offending service
docker compose restart <service>

# Analyze without restart
docker exec <container> ps aux
docker exec <container> top -b -n 1
```

---

## Disaster Recovery

### Full Restore from Backup

```bash
# Restore database
docker compose down
docker volume rm devsecops_postgres-data
docker compose up -d postgres

gunzip < backup.sql.gz | docker compose exec -T postgres \
  psql -U devsecops devsecops

# Restore other volumes/data as needed
docker compose up -d
```

### RTO/RPO Targets

- **RTO (Recovery Time Objective)**: 30 minutes
- **RPO (Recovery Point Objective)**: 1 hour
- **Backup Frequency**: Every 6 hours
- **Retention**: 30 days

---

## Support & Maintenance

Support office hours: [Your timezone]

For production issues:
- Email: support@yourdomain.com
- On-call: [Your contact]
- Status page: status.yourdomain.com
