# API Reference

Complete API documentation for DevSecOps Agent.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently using environment-based security. API key authentication coming in v2.

---

## Health Check

### GET /health/status
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-04-13T10:30:00Z",
  "components": {
    "api": "running",
    "monitoring": "running",
    "database": "connected"
  }
}
```

---

## Incidents

### GET /api/incidents
List incidents with optional filters.

**Query Parameters:**
- `status` (string): Filter by status (detected, analyzing, resolved)
- `severity` (string): Filter by severity (critical, high, medium, low)
- `limit` (integer): Max results (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 1,
    "title": "High CPU Usage - web-server",
    "severity": "high",
    "status": "resolved",
    "component": "web-server",
    "detected_at": "2024-04-13T10:25:00Z"
  }
]
```

### GET /api/incidents/{incident_id}
Get detailed incident information.

**Response:**
```json
{
  "incident_id": "inc_001",
  "title": "High CPU Usage - web-server",
  "description": "CPU usage exceeded 85% threshold",
  "severity": "high",
  "status": "resolved",
  "component": "web-server",
  "root_cause": "Memory leak in worker process",
  "remediation_action": "Restarted service",
  "detected_at": "2024-04-13T10:25:00Z",
  "resolved_at": "2024-04-13T10:30:00Z"
}
```

### GET /api/incidents/{incident_id}/timeline
Get incident timeline/events.

**Response:**
```json
[
  {
    "timestamp": "2024-04-13T10:25:00Z",
    "event": "Incident detected",
    "details": "CPU usage exceeded threshold"
  },
  {
    "timestamp": "2024-04-13T10:27:00Z",
    "event": "AI analysis complete",
    "details": "Root cause identified"
  }
]
```

---

## Remediation

### GET /api/remediation/rules
List active remediation rules.

**Response:**
```json
[
  {
    "rule_id": 1,
    "name": "High CPU Auto-Scale",
    "pattern": "container_cpu > 85",
    "action": "scale_up",
    "enabled": true
  }
]
```

### POST /api/remediation/execute
Execute remediation action.

**Request:**
```json
{
  "incident_id": "inc_001",
  "action": "restart_service",
  "dry_run": true
}
```

**Response:**
```json
{
  "status": "dry_run",
  "incident_id": "inc_001",
  "action": "restart_service",
  "would_execute": true,
  "estimated_duration": "30-60 seconds"
}
```

### GET /api/remediation/history
Get remediation execution history.

**Query Parameters:**
- `limit` (integer): Max results (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "incident_id": "inc_001",
    "action": "restart_service",
    "status": "success",
    "duration_seconds": 45,
    "executed_at": "2024-04-13T10:30:00Z"
  }
]
```

---

## Audit Reports

### GET /api/audit/generate
Generate comprehensive audit report.

**Response:**
```json
{
  "report_id": "audit_20240413_001",
  "status": "generating",
  "estimated_time": "2-3 minutes",
  "components": [
    "Infrastructure assessment",
    "Security scan",
    "Performance analysis"
  ]
}
```

### GET /api/audit/{report_id}/status
Get audit report status.

**Response:**
```json
{
  "report_id": "audit_20240413_001",
  "status": "completed",
  "completion_time": "2024-04-13T10:35:00Z",
  "findings": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 8
  }
}
```

### GET /api/audit/{report_id}/pdf
Download audit report as PDF.

Makes a GET request to retrieve PDF binary.

---

## Webhook

### POST /api/webhook/alert
Receive alerts from external systems.

**Request:**
```json
{
  "metric": "cpu_usage",
  "value": 95,
  "threshold": 80,
  "description": "Server CPU exceeded threshold"
}
```

**Response:**
```json
{
  "status": "received",
  "message": "Alert received and queued for analysis"
}
```

---

## System

### GET /api/status
Get system operational status.

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "timestamp": "2024-04-13T10:30:00Z",
  "features": {
    "auto_remediation": true,
    "slack_integration": true,
    "cve_scanner": true,
    "pdf_reports": true
  }
}
```

### GET /api/config
Get non-sensitive configuration.

**Response:**
```json
{
  "prometheus_url": "http://prometheus:9090",
  "monitor_interval": 30,
  "auto_remediation_enabled": true,
  "remediation_timeout": 300,
  "anomaly_threshold": 0.7
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error type",
  "detail": "Detailed error message"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad request
- `401`: Unauthorized
- `404`: Not found
- `500`: Server error
- `503`: Service unavailable

**Example Error:**
```json
{
  "error": "Not found",
  "detail": "Incident inc_999 not found"
}
```

---

## Rate Limiting

No rate limiting in v1.0, but planned for v2.0.

Recommended: <100 requests/minute per client.

---

## Pagination

List endpoints support pagination via query parameters:
- `offset` (integer): Start position
- `limit` (integer): Results per page

---

## Advanced Queries

### JavaScript Example
```javascript
const response = await fetch('http://localhost:8000/api/incidents?severity=high&status=detected');
const incidents = await response.json();
console.log(incidents);
```

### cURL Example
```bash
curl -X GET \
  'http://localhost:8000/api/incidents?severity=high&limit=10' \
  -H 'accept: application/json'
```

### Python Example
```python
import requests

response = requests.get(
    'http://localhost:8000/api/incidents',
    params={'severity': 'high', 'limit': 10}
)
incidents = response.json()
print(incidents)
```

---

## WebSocket Support

Planned for v2.0 - real-time incident streaming.

---

## GraphQL API

Planned for v2.0 - flexible query interface.

---

## Changelog

### v1.0.0 (Current)
- ✅ REST API complete
- ✅ Incident management
- ✅ Remediation execution
- ✅ Audit reports
- 🔄 WebSocket (v2.0)
- 🔄 GraphQL (v2.0)
