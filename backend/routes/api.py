"""
API Routes - Main API endpoints
"""

from typing import Dict, Any, List
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


@router.get("/incidents")
async def list_incidents() -> List[Dict[str, Any]]:
    """Get list of recent incidents"""
    from datetime import timedelta
    
    incidents = [
        {
            "id": 1,
            "title": "High CPU Usage - API Server",
            "severity": "high",
            "status": "resolved",
            "component": "api-server",
            "detected_at": datetime.utcnow().isoformat(),
            "resolved_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
        },
        {
            "id": 2,
            "title": "Memory Leak - Worker Service",
            "severity": "critical",
            "status": "resolved",
            "component": "worker-service",
            "detected_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "resolved_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
        },
        {
            "id": 3,
            "title": "Connection Pool Exhaustion",
            "severity": "medium",
            "status": "inProgress",
            "component": "database",
            "detected_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "resolved_at": None,
        },
    ]
    return incidents
