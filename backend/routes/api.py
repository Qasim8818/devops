"""
API Routes - Main API endpoints (Fake incidents removed)
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Body
from datetime import datetime

from config import get_settings
from advanced.cost_anomaly import CostAnomalyDetector
from advanced.cve_scanner import CVEScanner

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


@router.get("/cost/aws-anomaly")
async def aws_cost_anomaly():
    detector = CostAnomalyDetector()
    return await detector.analyze_aws_costs()


@router.get("/cost/gcp-anomaly")
async def gcp_cost_anomaly():
    detector = CostAnomalyDetector()
    return await detector.analyze_gcp_costs()


@router.get("/cost/forecast")
async def cost_forecast(days: int = 30):
    detector = CostAnomalyDetector()
    return await detector.get_cost_forecast(days_ahead=days)


@router.get("/cost/by-service")
async def cost_by_service(provider: str = "aws"):
    detector = CostAnomalyDetector()
    return await detector.get_cost_by_service(provider)

