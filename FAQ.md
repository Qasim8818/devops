# FAQ - Frequently Asked Questions

## Installation & Setup

### Q: Do I need to install dependencies locally?
**A:** No! Everything runs in Docker. Just ensure you have:
- Docker & Docker Compose
- 4GB RAM minimum
- Internet connection for pulling images

### Q: How do I customize the .env file?
**A:** 
1. Copy `.env.example` to `.env`
2. Edit values as needed
3. Never commit `.env` to git
4. For production, use secure vault instead

### Q: What if a port is already in use?
**A:** Change the port in `docker-compose.yml` or .env:
```bash
FASTAPI_PORT=8001  # Instead of 8000
```

---

## Monitoring & Metrics

### Q: How do I add custom Prometheus metrics?
**A:** Edit `monitoring/prometheus.yml` and add a scrape job:
```yaml
scrape_configs:
  - job_name: 'my-service'
    static_configs:
      - targets: ['localhost:9100']
```

### Q: Where are logs stored?
**A:** 
- Docker logs: `docker compose logs <service>`
- Application logs: `/app/logs/` (inside container)
- Loki: Queryable via Grafana

### Q: How do I export metrics to Grafana?
**A:** Already configured! Grafana can visualize Prometheus data at http://localhost:3000 (admin/admin)

---

## Incidents & Remediation

### Q: Why isn't my anomaly being detected?
**A:** Check:
1. Prometheus is scraping metrics: http://localhost:9090
2. Thresholds are configured correctly in `monitoring/alert_rules.yml`
3. Backend is running: `docker compose logs backend`

### Q: How do I enable auto-remediation?
**A:** Set in `.env`:
```bash
ENABLE_AUTO_REMEDIATION=true
COMMAND_EXECUTION_ALLOWED=true
```

### Q: Is auto-remediation safe?
**A:** Yes! Features include:
- Dry-run mode (default)
- Only runs whitelisted commands
- Critical actions require approval
- Full audit trail

---

## Slack Integration

### Q: How do I set up Slack notifications?
**A:** See [SETUP.md#slack-integration](SETUP.md#slack-integration)

Brief steps:
1. Create Slack app at api.slack.com
2. Get bot token (xoxb-...)
3. Create webhook URL
4. Update `.env` with credentials
5. Set `ENABLE_SLACK_INTEGRATION=true`

### Q: Why aren't alerts posting to Slack?
**A:** Check:
1. Webhook URL is correct
2. Bot token has `chat:write` permission
3. Logs: `docker compose logs backend | grep Slack`

---

## Performance

### Q: How many incidents can it handle?
**A:** Single instance: ~100K incidents/month. Scale with:
- More backend replicas: `docker compose up -d --scale backend=3`
- Larger database: Increase `DB_POOL_SIZE`
- Better hardware: Increase CPU/RAM

### Q: Why is response time slow?
**A:** Check:
1. CPU usage: `docker stats`
2. Database connections: `docker compose exec postgres psql -U devsecops -c "SELECT count(*) FROM pg_stat_activity;"`
3. Prometheus query time: http://localhost:9090/graph

### Q: How do I improve performance?
**A:** 
- Enable caching in backend
- Add database indexes
- Increase connection pool size
- Use read replicas for database

---

## Database

### Q: How do I backup the database?
**A:** 
```bash
# Backup
docker compose exec -T postgres pg_dump -U devsecops devsecops | gzip > backup.sql.gz

# Restore
gunzip < backup.sql.gz | docker compose exec -T postgres psql -U devsecops devsecops
```

### Q: How do I reset the database?
**A:** ⚠️ This deletes all data!
```bash
docker compose down -v
docker compose up -d postgres
docker compose exec backend alembic upgrade head
```

### Q: Can I use external PostgreSQL?
**A:** Yes! Set in `.env`:
```bash
DB_URL=postgresql://user:pass@external-db.com:5432/dbname
```

---

## Development

### Q: How do I run in development mode?
**A:** 
```bash
docker compose -f docker-compose.dev.yml up
```
Features:
- Hot reload for Python code
- Node hot reload for React
- Debug logging enabled

### Q: How do I add a new API endpoint?
**A:** 
1. Create new file in `backend/routes/`
2. Import in `backend/main.py`
3. Include router: `app.include_router(router, prefix="/api/path")`

### Q: How do I run tests?
**A:**
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
docker compose -f docker-compose.test.yml up
```

---

## Deployment

### Q: Can I deploy to Kubernetes?
**A:** Yes! See [DEPLOYMENT.md](DEPLOYMENT.md) for Helm charts.

### Q: What's the recommended way to deploy to AWS?
**A:** Use ECS + RDS. See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

### Q: How do I set up SSL/TLS?
**A:** Use Let's Encrypt with NGINX reverse proxy. See [DEPLOYMENT.md#ssl-tls-setup](DEPLOYMENT.md#ssl-tls-setup)

### Q: How do I scale to multiple servers?
**A:** Use Kubernetes or Docker Swarm. Single server max: ~10K incidents/hour.

---

## Security

### Q: Is it safe to expose to the internet?
**A:** Not yet (v1.0). Add:
- Authentication/OAuth2
- HTTPS/SSL
- Rate limiting
- Input validation
- IP whitelisting

Version 2.0 will include these by default.

### Q: Where should I store secrets?
**A:** Never in code. Use:
- Environment variables (.env, not in git)
- AWS Secrets Manager
- HashiCorp Vault
- GitHub Actions secrets

### Q: How do I audit who did what?
**A:** Audit logs are in database table `audit_logs`. Access via:
```sql
SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 100;
```

---

## Troubleshooting

### Q: "Connection refused" error
**A:** 
- Check service is running: `docker compose ps`
- Wait 30s for services to start
- Check logs: `docker compose logs <service>`

### Q: "Out of memory" error
**A:**
- Increase Docker memory limit
- Reduce Prometheus retention: `--storage.tsdb.retention.size=5GB`
- Disable unused features in .env

### Q: "Database connection failed"
**A:**
```bash
# Check password is correct in .env
# Restart database
docker compose restart postgres
# View logs
docker compose logs postgres
```

### Q: API returns 500 error
**A:**
```bash
# Check backend logs
docker compose logs backend

# Check database connection
docker compose exec backend python -c "from database import get_session; print('OK')"
```

---

## Contributing

### Q: How do I contribute?
**A:** See [CONTRIBUTING.md](CONTRIBUTING.md)

Steps:
1. Fork repository
2. Create feature branch
3. Make changes + tests
4. Open pull request
5. Address review comments

### Q: What should I work on?
**A:** See [ROADMAP.md](ROADMAP.md) for prioritized list of features.

Low-effort, high-impact:
- Documentation improvements
- Bug fixes
- Test coverage
- Performance optimizations

---

## Getting Help

- **Docs**: [README.md](README.md)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@yourdomain.com (once live)
- **Community**: DevSecOps community forums

---

*Last Updated: April 2024*
*Can't find your question? Open an issue or discussion!*
