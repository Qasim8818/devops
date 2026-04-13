# Quick Start Guide

Get the DevSecOps Agent running in 5 minutes.

## Prerequisites
- Docker & Docker Compose (v20.10+)
- Python 3.11+ (optional, for local development)
- 4GB RAM minimum
- Internet connection for pulling Docker images

## 1. Clone & Setup

```bash
git clone https://github.com/yourusername/devsecops-agent
cd devsecops-agent
cp .env.example .env
```

## 2. Verify Configuration

Edit `.env` if needed (default values work for local testing):

```bash
# Most important settings to configure
OLLAMA_API_URL=http://ollama:11434
LLM_MODEL=llama2
ENABLE_AUTO_REMEDIATION=true
DEBUG=false
```

## 3. Start Everything

```bash
docker compose up -d
```

Wait 30-60 seconds for all services to start.

## 4. Access the System

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | http://localhost:3001 | Main UI |
| **API Docs** | http://localhost:8000/docs | Interactive API |
| **Grafana** | http://localhost:3000 | Metrics visualization |
| **Prometheus** | http://localhost:9090 | Metrics data |

## 5. Verify Everything Works

```bash
# Check if agents are running
curl http://localhost:8000/health/status

# Check incidents (should be empty initially)
curl http://localhost:8000/api/incidents
```

## 6. Trigger Test Incident (Optional)

```bash
curl -X POST http://localhost:8000/api/webhook/alert \
  -H "Content-Type: application/json" \
  -d '{
    "metric": "cpu_usage",
    "value": 95,
    "threshold": 80,
    "description": "Test high CPU incident"
  }'
```

Check the dashboard - you should see the incident appear!

## Stopping

```bash
docker compose down

# To also remove data volumes
docker compose down -v
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker compose logs backend
docker compose logs ollama

# Restart everything
docker compose restart
```

### Out of memory
- Increase Docker memory limit (Settings → Resources)
- Or disable Ollama: comment out in docker-compose.yml

### Frontend not loading
```bash
# Check frontend logs
docker compose logs frontend

# Rebuild frontend
docker compose build frontend
docker compose up frontend
```

## Next Steps

1. Review [SETUP.md](SETUP.md) for detailed configuration
2. Check [API.md](API.md) for API reference
3. Configure Slack integration in `.env`
4. Review [CONTRIBUTING.md](CONTRIBUTING.md) for development

## Performance Targets

| Metric | Target |
|--------|--------|
| Anomaly Detection | < 2 seconds |
| Alert Delivery | < 10 seconds |
| Dashboard Load | < 1 second |
| API Response | < 500ms |

## Support

Found a bug? Open an issue on GitHub.
Questions? Check the [FAQ](FAQ.md).
