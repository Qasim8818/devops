"""
Remediation Routes - Production Grade
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import RemediationRule, Incident, get_session

router = APIRouter()

class RemediationRequest(BaseModel):
    """Request model for remediation execution"""
    incident_id: str
    action: str
    dry_run: bool = True

@router.get("/rules")
async def list_remediation_rules(
    enabled: bool = None,
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    """List all active remediation rules"""
    try:
        query = select(RemediationRule).order_by(RemediationRule.priority.desc())
        if enabled is not None:
            query = query.where(RemediationRule.enabled == enabled)
        result = await session.execute(query)
        rules = result.scalars().all()
        return [
            {
                "rule_id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "pattern": rule.pattern,
                "remediation_command": rule.remediation_command,
                "enabled": rule.enabled,
                "priority": rule.priority,
                "created_at": rule.created_at.isoformat() if rule.created_at else None,
                "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
            }
            for rule in rules
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list rules: {str(e)}")

@router.post("/execute")
async def execute_remediation(
    request: RemediationRequest,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Execute remediation action on an incident"""
    try:
        # Verify incident exists
        query = select(Incident).where(Incident.incident_id == request.incident_id)
        result = await session.execute(query)
        incident = result.scalar_one_or_none()
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {request.incident_id} not found")
        if request.dry_run:
            return {
                "status": "dry_run",
                "incident_id": request.incident_id,
                "action": request.action,
                "would_execute": True,
                "estimated_duration": "30-60 seconds",
                "timestamp": datetime.utcnow().isoformat(),
            }
        # Update incident remediation status
        incident.remediation_status = "running"
        incident.remediation_action = request.action
        incident.updated_at = datetime.utcnow()
        await session.commit()
        return {
            "status": "executing",
            "incident_id": request.incident_id,
            "action": request.action,
            "start_time": datetime.utcnow().isoformat(),
            "estimated_completion": "30 seconds",
        }
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to execute remediation: {str(e)}")

@router.get("/history")
async def remediation_history(
    incident_id: str = None,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    """Get remediation execution history"""
    try:
        query = select(Incident).where(
            (Incident.remediation_status.isnot(None)) &
            (Incident.remediation_action.isnot(None))
        ).order_by(Incident.updated_at.desc())
        if incident_id:
            query = query.where(Incident.incident_id == incident_id)
        query = query.limit(limit)
        result = await session.execute(query)
        incidents = result.scalars().all()
        return [
            {
                "id": incident.id,
                "incident_id": incident.incident_id,
                "action": incident.remediation_action,
                "status": incident.remediation_status,
                "duration_seconds": int((incident.resolved_at - incident.detected_at).total_seconds())
                                    if incident.resolved_at and incident.detected_at else None,
                "executed_at": incident.detected_at.isoformat() if incident.detected_at else None,
                "completed_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
            }
            for incident in incidents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")
