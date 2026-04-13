"""
Health Check Routes
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

router = APIRouter()


@router.get("/status")
async def health_status() -> Dict[str, Any]:
    """Application health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "running",
            "monitoring": "running",
            "database": "connected",
        },
    }


@router.get("/ready")
async def ready_check() -> Dict[str, bool]:
    """Readiness probe for Kubernetes"""
    return {"ready": True}


@router.get("/live")
async def liveness_check() -> Dict[str, bool]:
    """Liveness probe for Kubernetes"""
    return {"live": True}
