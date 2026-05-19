"""
Database configuration and models
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON
from datetime import datetime

from backend.config import get_settings



settings = get_settings()

# Async database setup
engine = create_async_engine(
    settings.DB_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


class Incident(Base):
    """Incident model"""
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True)
    incident_id = Column(String(255), unique=True, index=True)
    title = Column(String(500))
    description = Column(Text)
    severity = Column(String(50))  # critical, high, medium, low
    status = Column(String(50))  # detected, analyzing, remediating, resolved, failed
    component = Column(String(255))
    root_cause = Column(Text)
    ai_analysis = Column(JSON)
    remediation_action = Column(Text)
    remediation_status = Column(String(50))  # pending, running, success, failed
    metric_name = Column(String(255))
    metric_value = Column(Float)
    threshold = Column(Float)
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Metric(Base):
    """Metric history model"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(255), index=True)
    value = Column(Float)
    labels = Column(JSON)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    action = Column(String(255))
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    status = Column(String(50))
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class RemediationRule(Base):
    """Remediation rule model"""
    __tablename__ = "remediation_rules"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(Text)
    pattern = Column(String(500))  # Pattern to match anomalies
    remediation_command = Column(Text)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        yield session
