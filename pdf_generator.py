"""
PDF Report Generator using ReportLab.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime


# Brand colors
PRIMARY = colors.HexColor('#4F46E5')
ACCENT = colors.HexColor('#06B6D4')
SUCCESS = colors.HexColor('#10B981')
WARNING = colors.HexColor('#F59E0B')
DANGER = colors.HexColor('#EF4444')
LIGHT_GRAY = colors.HexColor('#F1F5F9')
DARK_TEXT = colors.HexColor('#1E293B')
MUTED = colors.HexColor('#64748B')


def score_color(score):
    if score >= 75:
        return SUCCESS
    elif score >= 50:
        return WARNING
    return DANGER


def generate_analysis_pdf(analysis, user):
    """Generate a PDF report for a resume analysis."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
        fontSize=22, fontName='Helvetica-Bold',
        textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=4)

    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontSize=11, textColor=MUTED, alignment=TA_CENTER, spaceAfter=20)

    section_style = ParagraphStyle('Section', parent=styles['Normal'],
        fontSize=13, fontName='Helvetica-Bold',
        textColor=PRIMARY, spaceBefore=16, spaceAfter=8)

    body_style = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=10, textColor=DARK_TEXT, spaceAfter=4, leading=16)

    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
        fontSize=10, textColor=DARK_TEXT, leftIndent=12,
        spaceAfter=3, leading=15, bulletIndent=4)

    # Header
    story.append(Paragraph("AI Resume Analysis Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
    story.append(Spacer(1, 16))

    # User & Resume Info
    story.append(Paragraph("Candidate Information", section_style))
    info_data = [
        ['Name:', user.get_full_name() or user.email],
        ['Email:', user.email],
        ['Resume:', analysis.resume.filename],
        ['Analysis Date:', analysis.created_at.strftime('%B %d, %Y')],
    ]
    info_table = Table(info_data, colWidths=[3*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), PRIMARY),
        ('TEXTCOLOR', (1, 0), (1, -1), DARK_TEXT),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # Scores
    story.append(Paragraph("Score Overview", section_style))
    score_data = [
        ['ATS Score', 'Resume Score'],
        [f"{analysis.ats_score:.0f}/100", f"{analysis.resume_score:.0f}/100"],
    ]
    score_table = Table(score_data, colWidths=[7.5*cm, 7.5*cm])
    score_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, 1), 22),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 1), (0, 1), score_color(analysis.ats_score)),
        ('TEXTCOLOR', (1, 1), (1, 1), score_color(analysis.resume_score)),
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('BACKGROUND', (0, 1), (-1, 1), LIGHT_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 16))

    # Summary
    story.append(Paragraph("Resume Summary", section_style))
    story.append(Paragraph(analysis.summary, body_style))
    story.append(Spacer(1, 8))

    def list_section(title, items, icon="•"):
        story.append(Paragraph(title, section_style))
        if items:
            for item in items:
                story.append(Paragraph(f"{icon} {item}", bullet_style))
        else:
            story.append(Paragraph("None identified.", body_style))
        story.append(Spacer(1, 4))

    list_section("✅ Strengths", analysis.strengths)
    list_section("⚠️ Weaknesses", analysis.weaknesses)
    list_section("📝 Grammar Suggestions", analysis.grammar_suggestions)
    list_section("🎨 Formatting Suggestions", analysis.formatting_suggestions)
    list_section("🔧 Missing Skills", analysis.missing_skills)
    list_section("🔑 Missing Keywords", analysis.missing_keywords)
    list_section("💡 AI Recommendations", analysis.ai_recommendations)

    # Footer note
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0')))
    story.append(Spacer(1, 8))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
        fontSize=9, textColor=MUTED, alignment=TA_CENTER)
    story.append(Paragraph(
        "Generated by AI Resume Analyzer • Powered by Google Gemini AI",
        footer_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
