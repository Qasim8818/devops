"""
Health Check Routes
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import text
from database import engine

router = APIRouter()


@router.get("/status")
async def health_status() -> Dict[str, Any]:
    """Application health status with real DB check"""
    db_status = "connected"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "running",
            "monitoring": "running",
            "database": db_status,
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

