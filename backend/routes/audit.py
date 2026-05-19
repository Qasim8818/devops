"""
Audit Report Routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import Dict, Any
from datetime import datetime
from backend.advanced.pdf_generator import PDFReportGenerator

import io

router = APIRouter()


@router.get("/generate")
async def generate_audit_report() -> Dict[str, Any]:
    """Generate comprehensive audit report"""
    
    return {
        "report_id": "audit_20260413_001",
        "status": "generating",
        "estimated_time": "2-3 minutes",
        "components": [
            "Infrastructure assessment",
            "Security scan",
            "Performance analysis",
            "Recommendations",
        ],
    }


@router.get("/{report_id}/status")
async def get_audit_status(report_id: str) -> Dict[str, Any]:
    """Get audit report generation status"""
    
    return {
        "report_id": report_id,
        "status": "completed",
        "completion_time": datetime.utcnow().isoformat(),
        "findings": {
            "critical": 0,
            "high": 2,
            "medium": 5,
            "low": 8,
        },
    }


@router.get("/{report_id}/pdf")
async def download_audit_pdf(report_id: str):
    """Download audit report as PDF"""
    # Example data; in production, fetch real findings and recommendations
    findings = {"critical": 0, "high": 2, "medium": 5, "low": 8}
    recommendations = [
        {"title": "Patch high severity CVEs", "description": "Apply patches immediately.", "effort": "High"},
        {"title": "Review medium/low findings", "description": "Address in next audit cycle.", "effort": "Low"},
    ]
    pdf_gen = PDFReportGenerator()
    pdf_bytes = pdf_gen.generate_audit_report(
        company_name="Acme Corp",
        audit_date=datetime.utcnow(),
        findings=findings,
        recommendations=recommendations,
    )
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"})
