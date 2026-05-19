"""
Configuration management with environment variables and validation
"""

from typing import List, Optional
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=None, case_sensitive=True)
    
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
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v or v in ("null", "None"):
                return ["*"]
            if v.startswith("["):
                import json
                return json.loads(v)
            return [h.strip() for h in v.split(",") if h.strip()]
        return v



@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
