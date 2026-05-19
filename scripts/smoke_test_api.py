import asyncio
from typing import Any, Dict

from fastapi.testclient import TestClient

import os
import sys

# Ensure repo root is importable so `backend.*` resolves when run as a script.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.main import app




def assert_keys(obj: Dict[str, Any], keys: list[str]):
    for k in keys:
        if k not in obj:
            raise AssertionError(f"Missing key {k} in response")


def main():
    with TestClient(app) as client:
        # Root
        r = client.get("/")
        assert r.status_code == 200

        # Health
        r = client.get("/health/status")
        assert r.status_code == 200
        assert_keys(r.json(), ["status", "components"])

        r = client.get("/health/ready")
        assert r.status_code == 200
        assert_keys(r.json(), ["ready"])

        r = client.get("/health/live")
        assert r.status_code == 200
        assert_keys(r.json(), ["live"])

        # API
        r = client.get("/api/status")
        assert r.status_code == 200
        assert_keys(r.json(), ["status", "version", "features"])

        r = client.get("/api/config")
        assert r.status_code == 200
        assert_keys(r.json(), ["prometheus_url", "monitor_interval"])

        # Incidents (DB-backed)
        r = client.get("/api/incidents")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

        # Remediation
        r = client.get("/api/remediation/rules")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

        r = client.post(
            "/api/remediation/execute",
            json={"incident_id": "nonexistent", "action": "noop", "dry_run": True},
        )
        assert r.status_code in (200, 404)

        # Audit
        r = client.get("/api/audit/generate")
        assert r.status_code == 200
        assert_keys(r.json(), ["report_id", "status"])

        r = client.get("/api/audit/audit_20260413_001/status")
        assert r.status_code == 200
        assert_keys(r.json(), ["report_id", "status"])

        r = client.get("/api/audit/audit_20260413_001/pdf")
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")

        # Webhook
        r = client.post(
            "/api/webhook/alert",
            json={"metric": "cpu_usage", "value": 95, "threshold": 80, "description": "test"},
        )
        assert r.status_code == 200
        assert_keys(r.json(), ["status", "message"])


if __name__ == "__main__":
    main()
