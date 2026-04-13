"""
DevSecOps Agent - Main Application
Production-grade self-healing infrastructure monitoring and remediation
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import Settings, get_settings
from core.monitoring import MonitoringEngine
from core.ai import AIEngine
from core.ai_alerting import AlertingEngine
from routes import api, health, incidents, audit, remediation
from database import init_db
from logger import setup_logging

# Setup logging
logger = setup_logging()

# Global app state
app_state = {
    "monitoring_engine": None,
    "ai_engine": None,
    "alerting_engine": None,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    settings = get_settings()
    
    logger.info("Starting DevSecOps Agent...")
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")
        
        # Initialize engines
        app_state["monitoring_engine"] = MonitoringEngine(settings)
        app_state["ai_engine"] = AIEngine(settings)
        app_state["alerting_engine"] = AlertingEngine(settings)
        
        # Start background tasks
        await app_state["monitoring_engine"].start()
        logger.info("Monitoring engine started")
        
        # Verify Ollama/LLM connection
        health = await app_state["ai_engine"].health_check()
        if not health["status"] == "healthy":
            logger.warning(f"AI Engine health: {health}")
        
        logger.info("✅ DevSecOps Agent ready")
        
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down DevSecOps Agent...")
    if app_state["monitoring_engine"]:
        await app_state["monitoring_engine"].stop()
    logger.info("Shutdown complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title="DevSecOps Agent API",
    description="Self-healing DevSecOps system with AI-powered incident response",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(remediation.router, prefix="/api/remediation", tags=["remediation"])


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "DevSecOps Agent",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health/status",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
