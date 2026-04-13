"""
Advanced Features - Slack Bot Integration
"""

from typing import Dict, Any
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from logger import setup_logging
from config import get_settings

logger = setup_logging()
settings = get_settings()


class SlackBotIntegration:
    """Slack bot for incident notifications and management"""
    
    def __init__(self):
        self.client = WebClient(token=settings.SLACK_BOT_TOKEN) if settings.SLACK_BOT_TOKEN else None
        self.channel = settings.SLACK_CHANNEL_ALERTS
    
    async def send_incident_alert(self, incident: Dict[str, Any]) -> bool:
        """Send incident alert to Slack"""
        
        if not self.client:
            logger.warning("Slack bot not configured")
            return False
        
        try:
            # Build incident summary
            summary = f"""
🚨 Infrastructure Incident Detected

*Component:* {incident.get('component', 'Unknown')}
*Severity:* {incident.get('severity', 'Unknown')}
*Description:* {incident.get('description', 'N/A')}
*Metric Value:* {incident.get('value', 'N/A')}
*Threshold:* {incident.get('threshold', 'N/A')}

_Detected at:_ {incident.get('detected_at', 'N/A')}
            """
            
            # Send to Slack
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=summary,
                blocks=[
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🛡️ DevSecOps Alert"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Component:*\n{incident.get('component', 'Unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Severity:*\n{incident.get('severity', 'Unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Metric:*\n{incident.get('metric', 'Unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Value:*\n{incident.get('value', 'N/A')}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Description:*\n{incident.get('description', 'N/A')}"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View Details"
                                },
                                "url": f"http://localhost:3001/incidents/{incident.get('id', '')}"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Auto Remediate"
                                },
                                "value": incident.get('id', ''),
                                "action_id": "auto_remediate"
                            }
                        ]
                    }
                ]
            )
            
            logger.info(f"Slack alert sent: {response['ts']}")
            return True
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e}")
            return False
    
    async def handle_slash_command(self, command: str, args: str) -> Dict[str, Any]:
        """Handle Slack slash commands"""
        
        commands = {
            "status": "System operational",
            "incidents": "No critical incidents in progress",
            "rules": "3 remediation rules active",
        }
        
        response = commands.get(command, f"Unknown command: {command}")
        return {"text": response}
