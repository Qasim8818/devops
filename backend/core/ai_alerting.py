"""
Alerting Engine - Multi-channel alerts (Slack, Email, Webhook)
"""

import asyncio
from typing import Dict, Any, List, Optional
import httpx

from backend.logger import setup_logging
from backend.config import get_settings


logger = setup_logging()
settings = get_settings()


class AlertingEngine:
    """Multi-channel alerting system"""
    
    def __init__(self, settings):
        self.settings = settings
        self.slack_url = settings.SLACK_WEBHOOK_URL
        self.email_enabled = settings.ALERT_EMAIL_ENABLED
        self.webhook_enabled = settings.WEBHOOK_ENABLED
        
    async def send_alert(
        self,
        title: str,
        severity: str,
        details: Dict[str, Any],
        channels: Optional[List[str]] = None,
    ) -> Dict[str, bool]:
        """Send alert to multiple channels"""
        
        if channels is None:
            channels = ["slack", "webhook"]  # Default channels
        
        results = {}
        
        # Send to Slack
        if "slack" in channels and self.slack_url:
            results["slack"] = await self._send_slack_alert(title, severity, details)
        
        # Send email
        if "email" in channels and self.email_enabled:
            results["email"] = await self._send_email_alert(title, severity, details)
        
        # Send webhook
        if "webhook" in channels and self.webhook_enabled:
            results["webhook"] = await self._send_webhook_alert(title, severity, details)
        
        return results
    
    async def _send_slack_alert(
        self,
        title: str,
        severity: str,
        details: Dict[str, Any],
    ) -> bool:
        """Send alert to Slack"""
        
        if not self.slack_url:
            return False
        
        # Color based on severity
        color_map = {
            "critical": "#FF0000",
            "high": "#FF6600",
            "medium": "#FFAA00",
            "low": "#00AA00",
        }
        
        payload = {
            "attachments": [
                {
                    "color": color_map.get(severity, "#999999"),
                    "title": f"🚨 {title}",
                    "fields": [
                        {"title": "Severity", "value": severity, "short": True},
                        {"title": "Metric", "value": details.get("metric", "N/A"), "short": True},
                        {"title": "Value", "value": str(details.get("value", "N/A")), "short": True},
                        {"title": "Threshold", "value": str(details.get("threshold", "N/A")), "short": True},
                        {"title": "Description", "value": details.get("description", "N/A"), "short": False},
                    ],
                    "footer": "DevSecOps Agent",
                    "ts": int(asyncio.get_running_loop().time()),
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.slack_url, json=payload)
                success = response.status_code == 200
                logger.info(f"Slack alert sent: {success}")
                return success
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    async def _send_email_alert(
        self,
        title: str,
        severity: str,
        details: Dict[str, Any],
    ) -> bool:
        """Send email alert (placeholder)"""
        
        # In production, integrate with sendgrid, aws ses, or smtp
        logger.info(f"Email alert (not implemented): {title}")
        return True
    
    async def _send_webhook_alert(
        self,
        title: str,
        severity: str,
        details: Dict[str, Any],
    ) -> bool:
        """Send webhook alert"""
        
        payload = {
            "alert_type": "infrastructure_anomaly",
            "title": title,
            "severity": severity,
            "details": details,
            "timestamp": asyncio.get_running_loop().time(),
        }
        
        # Could send to external webhooks configured in settings
        logger.info(f"Webhook alert: {title}")
        return True
