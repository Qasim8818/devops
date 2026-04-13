# 🛡️ Self-Healing DevSecOps Agent

> Autonomous infrastructure monitoring with AI-powered incident detection and self-remediation. **No human intervention required.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=flat&logo=docker)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb?style=flat&logo=react)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)

---

## 🚨 Problem

Engineering teams waste **hours manually responding** to incidents, misconfigurations, and security alerts. By the time a human gets paged, damage is already done.

## ✅ Solution

This agent watches your stack **24/7**, uses an LLM to understand what's wrong, and executes safe corrective actions — **automatically**.

---

## ⚡ Features

- 🔍 **Async real-time monitoring** — watches your infrastructure continuously
- 🤖 **AI-powered analysis** — Ollama LLM with rule-based fallback
- 🔧 **Safe auto-remediation** — executes fixes with guardrails
- 📣 **Multi-channel alerting** — Slack, email, webhook
- 🌐 **REST API** — FastAPI with interactive docs
- 📊 **Live dashboard** — React frontend for visibility
- 🐳 **Full observability** — Prometheus + Grafana + Loki
- 🔄 **CI/CD pipeline** — GitHub Actions included

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, AsyncIO |
| AI Engine | Ollama LLM + Rule-based fallback |
| Monitoring | Prometheus, Grafana, Loki |
| Containers | Docker, Docker Compose |
| Frontend | React 18, Tailwind CSS |
| CI/CD | GitHub Actions |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- 4GB RAM minimum

### Run It

```bash
git clone https://github.com/YOURUSERNAME/devsecops-agent
cd devsecops-agent
cp .env.example .env
docker compose up -d
```

### Access

| Service | URL |
|---|---|
| **Dashboard** | http://localhost:3001 |
| **API Docs** | http://localhost:8000/docs |
| **Grafana** | http://localhost:3000 (admin/admin) |
| **Prometheus** | http://localhost:9090 |

---

## 📈 Performance

- ⚡ Anomaly detection in **under 2 seconds**
- 🔧 Auto-remediation triggered in **under 30 seconds**
- 🛡️ Zero manual intervention for common failure patterns

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/status` | System health check |
| GET | `/api/incidents` | List recent incidents |
| POST | `/api/remediation/execute` | Trigger remediation |
| GET | `/api/audit/generate` | Generate audit report |

---

## 📚 Documentation

- **[Quick Start](QUICKSTART.md)** — Get running in 5 minutes
- **[Setup Guide](SETUP.md)** — Detailed configuration
- **[API Docs](API.md)** — Complete API reference
- **[Deployment](DEPLOYMENT.md)** — Production strategies
- **[Contributing](CONTRIBUTING.md)** — Developer guide

---

## 🔒 Safety First

- ✅ Runs whitelisted commands only
- ✅ Dry-run mode by default
- ✅ Full audit trail of every action
- ✅ No external API dependencies
- ✅ Rule-based fallback if LLM fails

---

## 💼 Consulting & Custom Work

I build custom DevSecOps pipelines and autonomous incident response systems for engineering teams.

📩 **Email**: [YOUR EMAIL HERE]  
💼 **LinkedIn**: [YOUR LINKEDIN URL]  
🔗 **Website**: [YOUR WEBSITE]

---

## 📄 License

MIT License — See [LICENSE](LICENSE) file for details.

---

## 🙏 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Built with ❤️ for autonomous infrastructure management**
