import io
import json
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    PageBreak,
)


def generate_pdf_report(analysis: dict) -> bytes:
    """Generate a professional PDF report from analysis results."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "LexTitle",
        parent=styles["Title"],
        fontSize=28,
        textColor=colors.HexColor("#0a0f1e"),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "LexSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    section_style = ParagraphStyle(
        "LexSection",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#0a0f1e"),
        spaceBefore=20,
        spaceAfter=10,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "LexBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14,
    )
    bullet_style = ParagraphStyle(
        "LexBullet",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        leftIndent=20,
        spaceAfter=6,
        leading=14,
        bulletIndent=8,
    )
    gold_style = ParagraphStyle(
        "LexGold",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#f5c518"),
    )
    footer_style = ParagraphStyle(
        "LexFooter",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#999999"),
        alignment=TA_CENTER,
    )

    elements = []

    # === HEADER ===
    elements.append(Paragraph("LEXAI", title_style))
    elements.append(Paragraph("Agentic AI for Autonomous Legal Case Analysis", subtitle_style))
    elements.append(
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#f5c518"), spaceAfter=20)
    )
    elements.append(
        Paragraph(
            f"Report Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            subtitle_style,
        )
    )

    # === CASE CLASSIFICATION ===
    classification = analysis.get("classification", {})
    elements.append(Paragraph("1. CASE CLASSIFICATION", section_style))
    elements.append(
        Paragraph(
            f"<b>Case Type:</b> {classification.get('case_type', 'N/A')}",
            body_style,
        )
    )
    elements.append(
        Paragraph(
            f"<b>Confidence:</b> {classification.get('confidence', 'N/A')}%",
            body_style,
        )
    )

    # === CASE SUMMARY ===
    summary = analysis.get("summary", {})
    elements.append(Paragraph("2. CASE SUMMARY", section_style))
    elements.append(Paragraph(summary.get("summary", "N/A"), body_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<b>What Happened:</b> {summary.get('what_happened', 'N/A')}", body_style))
    elements.append(Paragraph(f"<b>Parties Involved:</b> {summary.get('parties_involved', 'N/A')}", body_style))
    elements.append(Paragraph(f"<b>Dispute:</b> {summary.get('dispute', 'N/A')}", body_style))

    # === KEY ISSUES ===
    key_issues = analysis.get("key_issues", {}).get("issues", [])
    elements.append(Paragraph("3. KEY LEGAL ISSUES", section_style))
    if key_issues:
        for idx, issue in enumerate(key_issues, 1):
            elements.append(Paragraph(f"{idx}. {issue}", bullet_style))
    else:
        elements.append(Paragraph("No key issues identified.", body_style))

    # === PARTIES ===
    parties = analysis.get("parties", {})
    elements.append(Paragraph("4. PARTIES INVOLVED", section_style))
    elements.append(Paragraph(f"<b>Plaintiff:</b> {parties.get('plaintiff', 'N/A')}", body_style))
    elements.append(Paragraph(f"<b>Defendant:</b> {parties.get('defendant', 'N/A')}", body_style))
    lawyers = parties.get("lawyers", [])
    if lawyers:
        elements.append(Paragraph(f"<b>Lawyers:</b> {', '.join(lawyers)}", body_style))
    elements.append(Paragraph(f"<b>Judge:</b> {parties.get('judge', 'N/A')}", body_style))

    # === TIMELINE ===
    timeline = analysis.get("timeline", {}).get("timeline", [])
    elements.append(Paragraph("5. CASE TIMELINE", section_style))
    if timeline:
        table_data = [["Date", "Event"]]
        for item in timeline:
            table_data.append([item.get("date", "N/A"), item.get("event", "N/A")])
        t = Table(table_data, colWidths=[3.5 * cm, 13.5 * cm])
        t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a0f1e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f8f8")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        elements.append(t)
    else:
        elements.append(Paragraph("No timeline data available.", body_style))

    # === RISK ANALYSIS ===
    risk = analysis.get("risk_analysis", {})
    elements.append(Paragraph("6. RISK ANALYSIS", section_style))

    p_risk = risk.get("plaintiff_risk", {})
    d_risk = risk.get("defendant_risk", {})

    elements.append(Paragraph(f"<b>Plaintiff Risk Score: {p_risk.get('score', 'N/A')}/100</b>", body_style))
    elements.append(Paragraph(p_risk.get("reasoning", "N/A"), body_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>Defendant Risk Score: {d_risk.get('score', 'N/A')}/100</b>", body_style))
    elements.append(Paragraph(d_risk.get("reasoning", "N/A"), body_style))

    # === MISSING EVIDENCE ===
    missing = analysis.get("missing_evidence", {})
    elements.append(Paragraph("7. MISSING EVIDENCE & GAPS", section_style))

    missing_docs = missing.get("missing_documents", [])
    if missing_docs:
        elements.append(Paragraph("<b>Missing Documents:</b>", body_style))
        for doc_item in missing_docs:
            elements.append(Paragraph(f"\u2022 {doc_item}", bullet_style))

    weak_args = missing.get("weak_arguments", [])
    if weak_args:
        elements.append(Paragraph("<b>Weak Arguments:</b>", body_style))
        for arg in weak_args:
            elements.append(Paragraph(f"\u2022 {arg}", bullet_style))

    gaps = missing.get("gaps", [])
    if gaps:
        elements.append(Paragraph("<b>Case Gaps:</b>", body_style))
        for gap in gaps:
            elements.append(Paragraph(f"\u2022 {gap}", bullet_style))

    # === RECOMMENDATIONS ===
    recommendations = analysis.get("recommendations", {}).get("recommendations", [])
    elements.append(Paragraph("8. RECOMMENDATIONS", section_style))
    if recommendations:
        for idx, rec in enumerate(recommendations, 1):
            elements.append(Paragraph(f"<b>{idx}.</b> {rec}", bullet_style))
    else:
        elements.append(Paragraph("No recommendations available.", body_style))

    # === SIMILAR CASES ===
    similar = analysis.get("similar_cases", {}).get("similar_cases", [])
    elements.append(Paragraph("9. SIMILAR LANDMARK CASES", section_style))
    if similar:
        for idx, case in enumerate(similar, 1):
            elements.append(
                Paragraph(
                    f"<b>{idx}. {case.get('name', 'N/A')} ({case.get('year', 'N/A')})</b>",
                    body_style,
                )
            )
            elements.append(Paragraph(f"<b>Outcome:</b> {case.get('outcome', 'N/A')}", body_style))
            elements.append(Paragraph(f"<b>Relevance:</b> {case.get('relevance', 'N/A')}", body_style))
            elements.append(Spacer(1, 8))
    else:
        elements.append(Paragraph("No similar cases identified.", body_style))

    # === DISCLAIMER ===
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceAfter=10))
    elements.append(
        Paragraph(
            "<b>DISCLAIMER:</b> This report is generated by LexAI, an AI-powered legal analysis tool. "
            "The analysis, recommendations, and risk scores are for informational purposes only and do not "
            "constitute legal advice. Always consult a qualified legal professional before making legal decisions.",
            ParagraphStyle("Disclaimer", parent=body_style, fontSize=8, textColor=colors.HexColor("#999999")),
        )
    )
    elements.append(Spacer(1, 10))
    elements.append(
        Paragraph(
            f"Generated by LexAI \u2014 {datetime.now().strftime('%d %B %Y')}",
            footer_style,
        )
    )

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
