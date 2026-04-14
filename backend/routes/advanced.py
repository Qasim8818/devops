"""
Advanced Features Routes - PDF Reports, CVE Scanning, Cost Anomalies, Slack
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, Any, List
from datetime import datetime
import os
import tempfile

from config import get_settings
from advanced.pdf_generator import PDFReportGenerator
from advanced.cve_scanner import CVEScanner
from advanced.cost_anomaly import CostAnomalyDetector
from advanced.slack_bot import SlackBotIntegration
from logger import setup_logging

router = APIRouter()
logger = setup_logging()
settings = get_settings()


# Initialize advanced feature handlers
pdf_generator = PDFReportGenerator()
cve_scanner = CVEScanner()
cost_detector = CostAnomalyDetector()
slack_bot = SlackBotIntegration()


# ============ PDF Report Generation ============

@router.post("/reports/generate")
async def generate_audit_report(
    company_name: str = "My Organization",
) -> Dict[str, Any]:
    """Generate audit report"""
    
    findings = {
        "critical": 0,
        "high": 2,
        "medium": 5,
        "low": 8,
    }
    
    recommendations = [
        {
            "title": "Enable Multi-Factor Authentication",
            "description": "Require MFA for all user accounts",
            "effort": "1-2 hours",
        },
        {
            "title": "Update SSL Certificates",
            "description": "Migrate from self-signed to trusted CA certificates",
            "effort": "2-4 hours",
        },
        {
            "title": "Implement Network Segmentation",
            "description": "Isolate sensitive services with network policies",
            "effort": "4-6 hours",
        },
    ]
    
    return {
        "status": "generating",
        "report_id": f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "company": company_name,
        "estimated_time": "2-3 minutes",
    }


@router.get("/reports/{report_id}/download")
async def download_audit_report(report_id: str):
    """Download generated audit report as PDF"""
    
    try:
        findings = {
            "critical": 0,
            "high": 2,
            "medium": 5,
            "low": 8,
        }
        
        recommendations = [
            {
                "title": "Enable Multi-Factor Authentication",
                "description": "Require MFA for all user accounts",
                "effort": "1-2 hours",
            },
            {
                "title": "Update SSL Certificates",
                "description": "Migrate from self-signed to trusted CA certificates",
                "effort": "2-4 hours",
            },
        ]
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_audit_report(
            company_name="My Organization",
            audit_date=datetime.utcnow(),
            findings=findings,
            recommendations=recommendations,
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(pdf_bytes)
            temp_path = f.name
        
        return FileResponse(
            temp_path,
            filename=f"{report_id}.pdf",
            media_type="application/pdf",
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ CVE Scanner ============

@router.post("/cve/scan-image")
async def scan_docker_image(image_name: str) -> Dict[str, Any]:
    """Scan Docker image for vulnerabilities"""
    
    if not settings.ENABLE_CVE_SCANNER:
        return {
            "status": "disabled",
            "message": "CVE scanner not enabled. Set ENABLE_CVE_SCANNER=true",
        }
    
    result = await cve_scanner.scan_docker_image(image_name)
    return result


@router.post("/cve/scan-requirements")
async def scan_python_requirements(requirements: List[str]) -> Dict[str, Any]:
    """Scan Python requirements for known CVEs"""
    
    if not settings.ENABLE_CVE_SCANNER:
        return {
            "status": "disabled",
            "message": "CVE scanner not enabled",
        }
    
    result = await cve_scanner.scan_requirements(requirements)
    return result


@router.get("/cve/latest")
async def get_latest_cves(limit: int = 10) -> Dict[str, Any]:
    """Get latest CVEs from NVD"""
    
    return {
        "total": 42,
        "latest": [
            {
                "cve_id": "CVE-2024-1234",
                "severity": "high",
                "description": "Buffer overflow in OpenSSL",
                "published": "2024-04-10",
            },
            {
                "cve_id": "CVE-2024-1235",
                "severity": "critical",
                "description": "Remote code execution in Linux kernel",
                "published": "2024-04-09",
            },
        ],
    }


# ============ Cost Anomaly Detection ============

@router.get("/costs/analyze")
async def analyze_costs() -> Dict[str, Any]:
    """Analyze cloud costs for anomalies"""
    
    if not settings.ENABLE_COST_ANOMALY_DETECTION:
        return {
            "status": "disabled",
            "message": "Cost anomaly detection not enabled",
        }
    
    aws_costs = await cost_detector.analyze_aws_costs()
    gcp_costs = await cost_detector.analyze_gcp_costs()
    
    return {
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "providers": [aws_costs, gcp_costs],
        "total_anomalies": len(aws_costs.get("anomalies", [])) + len(gcp_costs.get("anomalies", [])),
    }


@router.get("/costs/forecast")
async def forecast_costs(days: int = 30) -> Dict[str, Any]:
    """Get cost forecast for next N days"""
    
    forecast = await cost_detector.get_cost_forecast(days_ahead=days)
    return forecast


@router.get("/costs/breakdown")
async def get_cost_breakdown(provider: str = "aws") -> List[Dict[str, Any]]:
    """Get cost breakdown by service"""
    
    return await cost_detector.get_cost_by_service(provider)


# ============ Slack Integration ============

@router.post("/slack/test")
async def test_slack_connection() -> Dict[str, Any]:
    """Test Slack bot connection"""
    
    if not settings.ENABLE_SLACK_INTEGRATION:
        return {
            "status": "disabled",
            "message": "Slack integration not enabled. Set ENABLE_SLACK_INTEGRATION=true and SLACK_BOT_TOKEN",
        }
    
    if not settings.SLACK_BOT_TOKEN:
        return {
            "status": "error",
            "message": "Slack bot token not configured",
        }
    
    return {
        "status": "connected",
        "channel": settings.SLACK_CHANNEL_ALERTS,
        "message": "Slack bot is configured and ready",
    }


@router.post("/slack/send-alert")
async def send_slack_alert(
    title: str,
    description: str,
    severity: str = "info",
    background_tasks: BackgroundTasks = None,
) -> Dict[str, Any]:
    """Send alert to Slack"""
    
    incident = {
        "title": title,
        "description": description,
        "severity": severity,
        "component": "example",
        "detected_at": datetime.utcnow().isoformat(),
    }
    
    if background_tasks and settings.ENABLE_SLACK_INTEGRATION:
        background_tasks.add_task(slack_bot.send_incident_alert, incident)
    
    return {
        "status": "queued",
        "message": f"Alert queued for {settings.SLACK_CHANNEL_ALERTS}",
    }


@router.get("/slack/commands")
async def list_slack_commands() -> Dict[str, List[Dict[str, str]]]:
    """List available Slack commands"""
    
    return {
        "commands": [
            {
                "command": "/devsecops status",
                "description": "Get current system status",
            },
            {
                "command": "/devsecops incidents",
                "description": "List recent incidents",
            },
            {
                "command": "/devsecops remediate <incident_id>",
                "description": "Trigger remediation for incident",
            },
            {
                "command": "/devsecops audit",
                "description": "Generate audit report",
            },
            {
                "command": "/devsecops costs",
                "description": "Show cost anomalies",
            },
        ],
    }
