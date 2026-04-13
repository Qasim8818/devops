"""
API Routes - Main API endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from config import get_settings
from database import get_session, Incident

router = APIRouter()
settings = get_settings()


@router.get("/status")
async def api_status() -> Dict[str, Any]:
    """Get API status"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "auto_remediation": settings.ENABLE_AUTO_REMEDIATION,
            "slack_integration": settings.ENABLE_SLACK_INTEGRATION,
            "cve_scanner": settings.ENABLE_CVE_SCANNER,
            "pdf_reports": settings.ENABLE_PDF_REPORTS,
        },
    }


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    """Get non-sensitive configuration"""
    return {
        "prometheus_url": settings.PROMETHEUS_URL,
        "monitor_interval": settings.MONITOR_INTERVAL,
        "auto_remediation_enabled": settings.ENABLE_AUTO_REMEDIATION,
        "remediation_timeout": settings.REMEDIATION_TIMEOUT,
        "anomaly_threshold": settings.ANOMALY_SCORE_THRESHOLD,
    }


@router.post("/webhook/alert")
async def receive_webhook_alert(payload: Dict[str, Any]) -> Dict[str, str]:
    """Receive webhook alerts from external sources"""
    return {
        "status": "received",
        "message": "Alert received and queued for analysis",
    }
