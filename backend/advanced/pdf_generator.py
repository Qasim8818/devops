"""
Advanced Features - PDF Report Generator
"""

from typing import Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
import io


class PDFReportGenerator:
    """Generate professional audit reports as PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    def generate_audit_report(
        self,
        company_name: str,
        audit_date: datetime,
        findings: Dict[str, Any],
        recommendations: list,
    ) -> bytes:
        """Generate comprehensive audit report as PDF"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch,
        )
        
        # Build content
        content = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=30,
        )
        content.append(Paragraph("🛡️ DevSecOps Audit Report", title_style))
        content.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        content.append(Paragraph("Executive Summary", self.styles['Heading2']))
        content.append(Spacer(1, 0.2*inch))
        
        summary_text = f"""
        <b>Organization:</b> {company_name}<br/>
        <b>Audit Date:</b> {audit_date.strftime('%Y-%m-%d')}<br/>
        <b>Report Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}<br/>
        """
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 0.3*inch))
        
        # Findings Summary
        content.append(Paragraph("Findings Summary", self.styles['Heading2']))
        content.append(Spacer(1, 0.2*inch))
        
        findings_data = [
            ['Severity', 'Count', 'Action Required'],
            ['Critical', str(findings.get('critical', 0)), 'Immediate'],
            ['High', str(findings.get('high', 0)), 'Within 7 days'],
            ['Medium', str(findings.get('medium', 0)), 'Within 30 days'],
            ['Low', str(findings.get('low', 0)), 'On next review'],
        ]
        
        findings_table = Table(findings_data, colWidths=[1.5*inch, 1.5*inch, 2*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        content.append(findings_table)
        content.append(Spacer(1, 0.5*inch))
        
        # Page break for recommendations
        content.append(PageBreak())
        
        # Recommendations
        content.append(Paragraph("Recommendations", self.styles['Heading2']))
        content.append(Spacer(1, 0.2*inch))
        
        for i, rec in enumerate(recommendations[:10], 1):  # Top 10
            content.append(Paragraph(
                f"<b>{i}. {rec.get('title', 'N/A')}</b>",
                self.styles['Heading3']
            ))
            content.append(Paragraph(rec.get('description', ''), self.styles['Normal']))
            content.append(Paragraph(
                f"<i>Estimated Effort: {rec.get('effort', 'Unknown')}</i>",
                self.styles['Italic']
            ))
            content.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
