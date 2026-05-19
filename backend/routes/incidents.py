"""
Incident Routes - Production Grade
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import Incident, get_session


router = APIRouter()

@router.get("")
async def list_incidents(
    status: str = Query(None),
    severity: str = Query(None),
    limit: int = Query(100, le=1000),
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    """List incidents with optional filtering by status and severity"""
    try:
        query = select(Incident).order_by(desc(Incident.detected_at))
        if status:
            query = query.where(Incident.status == status)
        if severity:
            query = query.where(Incident.severity == severity)
        query = query.limit(limit)
        result = await session.execute(query)
        incidents = result.scalars().all()
        return [
            {
                "id": incident.id,
                "incident_id": incident.incident_id,
                "title": incident.title,
                "severity": incident.severity,
                "status": incident.status,
                "component": incident.component,
                "detected_at": incident.detected_at.isoformat() if incident.detected_at else None,
                "metric_name": incident.metric_name,
                "metric_value": incident.metric_value,
            }
            for incident in incidents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list incidents: {str(e)}")

@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get full incident details"""
    try:
        query = select(Incident).where(Incident.incident_id == incident_id)
        result = await session.execute(query)
        incident = result.scalar_one_or_none()
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
        return {
            "id": incident.id,
            "incident_id": incident.incident_id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "status": incident.status,
            "component": incident.component,
            "root_cause": incident.root_cause,
            "ai_analysis": incident.ai_analysis,
            "remediation_action": incident.remediation_action,
            "remediation_status": incident.remediation_status,
            "metric_name": incident.metric_name,
            "metric_value": incident.metric_value,
            "threshold": incident.threshold,
            "detected_at": incident.detected_at.isoformat() if incident.detected_at else None,
            "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get incident: {str(e)}")

@router.get("/{incident_id}/timeline")
async def get_incident_timeline(
    incident_id: str,
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    """Get incident event timeline"""
    try:
        query = select(Incident).where(Incident.incident_id == incident_id)
        result = await session.execute(query)
        incident = result.scalar_one_or_none()
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
        timeline = [
            {
                "timestamp": incident.detected_at.isoformat() if incident.detected_at else None,
                "event": "Incident detected",
                "details": f"{incident.metric_name}: {incident.metric_value} (threshold: {incident.threshold})",
            },
        ]
        if incident.ai_analysis:
            timeline.append({
                "timestamp": (incident.detected_at + timedelta(seconds=5)).isoformat(),
                "event": "AI analysis complete",
                "details": str(incident.ai_analysis),
            })
        if incident.remediation_action:
            timeline.append({
                "timestamp": (incident.detected_at + timedelta(seconds=10)).isoformat(),
                "event": "Remediation applied",
                "details": incident.remediation_action,
            })
        if incident.resolved_at:
            timeline.append({
                "timestamp": incident.resolved_at.isoformat(),
                "event": "Incident resolved",
                "details": f"Status: {incident.remediation_status}",
            })
        return timeline
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timeline: {str(e)}")
