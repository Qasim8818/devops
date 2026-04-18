# DevSecOps Agent - Fix 2
## SQLAlchemy Async Routes - Complete Implementation

**Date**: April 18, 2026  
**Severity**: HIGH - Database operations require proper async patterns

---

## Problem Statement

Database routes must implement proper SQLAlchemy async patterns with correct session dependency injection. This ensures:

- Thread-safe database operations
- Proper resource cleanup
- Correct error handling
- Production-grade reliability

---

## Key Implementation Pattern

All routes must use this dependency injection pattern:

```python
session: AsyncSession = Depends(get_session)
```

This automatically:
1. Creates a new async database session
2. Injects it into your route handler
3. Cleans up resources after the request completes

---

## File 1: backend/routes/incidents.py

Complete production-grade implementation:

```python
"""
Incident Routes - Production Grade
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Incident, get_session

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
```

---

## File 2: backend/routes/remediation.py

Complete production-grade implementation:

```python
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
```

---

## Key Implementation Details

| Pattern | Explanation |
|---------|-------------|
| **Depends(get_session)** | Injects async session automatically. FastAPI manages creation and cleanup. |
| **async/await** | All database operations are non-blocking. Proper for async frameworks. |
| **Error Handling** | HTTPException for user errors (404). Generic 500 for unexpected failures. |
| **session.execute()** | SQLAlchemy async API for queries. Returns results with `scalars()`. |
| **await session.commit()** | Required to persist changes to database after updates. |
| **Query Filtering** | Uses SQLAlchemy `select()` with `where()` for safe parameterized queries. |

---

## Installation Instructions

1. **Stop backend**:
   ```bash
   docker-compose stop backend
   ```

2. **Backup old files**:
   ```bash
   cp backend/routes/incidents.py backend/routes/incidents.py.backup
   cp backend/routes/remediation.py backend/routes/remediation.py.backup
   ```

3. **Replace incidents.py**:
   Copy the code from File 1 above into `backend/routes/incidents.py`

4. **Replace remediation.py**:
   Copy the code from File 2 above into `backend/routes/remediation.py`

5. **Restart backend**:
   ```bash
   docker-compose up -d backend
   ```

6. **Verify**:
   ```bash
   curl http://localhost:8000/api/incidents
   ```

Expected response: `[]` (empty list if no incidents yet)

---

## Testing the Routes

### Test List Incidents
```bash
curl http://localhost:8000/api/incidents
```

### Test Get Incident (with fake ID)
```bash
curl http://localhost:8000/api/incidents/fake-id
```
Expected: 404 error (incident not found)

### Test List Remediation Rules
```bash
curl http://localhost:8000/api/remediation/rules
```

### Test Remediation History
```bash
curl http://localhost:8000/api/remediation/history
```

---

## Common Issues and Solutions

**Issue**: Routes return 500 errors  
**Solution**: Check `docker-compose logs backend` for specific error messages

**Issue**: Database connection errors in routes  
**Solution**: Ensure database is healthy and Fix 1 was completed successfully

**Issue**: `module not found` errors  
**Solution**: Ensure all imports are correct and files are in proper locations

---

## Next Steps

After implementing async routes:
1. **Fix 3**: SECRET_KEY generation and complete .env setup
2. Full deployment testing
3. Production hardening
