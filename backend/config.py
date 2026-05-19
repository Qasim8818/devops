"""
Configuration management with environment variables and validation
"""

from typing import List, Optional
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # If a .env exists but is malformed/missing quotes for list fields,
    # pydantic-settings may raise before app start. Keep defaults safe.

    """Application settings"""
    
    # API
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Ollama/LLM
    OLLAMA_API_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama2"
    LLM_TIMEOUT: int = 30
    LLM_FALLBACK_MODE: bool = True  # Use rule-based when LLM fails
    
    # Prometheus
    PROMETHEUS_URL: str = "http://prometheus:9090"
    PROMETHEUS_SCRAPE_INTERVAL: int = 15  # seconds
    
    # Loki
    LOKI_URL: str = "http://loki:3100"
    
    # Database
    DB_URL: str = "postgresql://devsecops:changeme@postgres:5432/devsecops"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Slack Integration
    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_CHANNEL_ALERTS: str = "#devsecops-alerts"
    
    # Email Alerting
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_EMAIL_FROM: str = "alerts@devsecops.local"
    ALERT_EMAIL_SMTP_HOST: str = "localhost"
    ALERT_EMAIL_SMTP_PORT: int = 587
    ALERT_EMAIL_PASSWORD: Optional[str] = None
    
    # Webhook
    WEBHOOK_ENABLED: bool = True
    WEBHOOK_TIMEOUT: int = 10
    
    # Monitoring
    MONITOR_INTERVAL: int = 30  # seconds
    HEALTH_CHECK_INTERVAL: int = 60  # seconds
    INCIDENT_RETENTION_DAYS: int = 30
    
    # Auto-remediation
    ENABLE_AUTO_REMEDIATION: bool = True
    REMEDIATION_TIMEOUT: int = 300  # 5 minutes
    REMEDIATION_RETRY_COUNT: int = 3
    
    # Feature flags
    ENABLE_SLACK_INTEGRATION: bool = False
    ENABLE_CVE_SCANNER: bool = False
    ENABLE_COST_ANOMALY_DETECTION: bool = False
    ENABLE_PDF_REPORTS: bool = True
    
    # Security
    COMMAND_EXECUTION_ALLOWED: bool = False  # Require explicit enable
    SAFE_COMMANDS_ONLY: bool = True
    
    # AI Model thresholds
    ANOMALY_SCORE_THRESHOLD: float = 0.7
    CONFIDENCE_THRESHOLD: float = 0.8
    
    class Config:
        # Disable env file loading by default; client deployments can still
        # provide env vars directly. This prevents crashes when a local .env
        # is present but malformed.
        env_file = None
        case_sensitive = True

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            # Use only environment variables + init settings.
            # Avoid DotEnvSettingsSource entirely.
            return (init_settings, env_settings)



        @staticmethod
        def parse_env_var(field_name: str, raw_value: str):
            """Harden env parsing for list fields like ALLOWED_HOSTS.

            Allows:
            - ALLOWED_HOSTS="*" (or comma-separated)
            - ALLOWED_HOSTS="[\"a.com\",\"b.com\"]" (JSON)
            """
            if field_name == "ALLOWED_HOSTS":
                value = (raw_value or "").strip()
                if value in ("", "null", "None"):
                    return ["*"]
                # Try JSON first
                try:
                    import json
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
                # Fallback to comma-separated
                return [v.strip() for v in value.split(",") if v.strip()]

            return raw_value



@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
