"""
PDF Report Generator Module
Generates downloadable PDF reports for daily and weekly summaries.
"""

import io
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFReportGenerator:
    """Generates PDF reports from daily/weekly data."""

    @staticmethod
    def generate_daily_report_pdf(
        report: Dict[str, Any], flat_id: str = "flat_001"
    ) -> bytes:
        """
        Generate a PDF for a single daily report.

        Args:
            report: Report dictionary from storage
            flat_id: Flat identifier

        Returns:
            PDF as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1f77b4"),
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#333333"),
            spaceAfter=6,
        )

        # Title
        report_date = datetime.fromisoformat(report["report_timestamp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        story.append(Paragraph(f"💧 Daily Water Usage Report", title_style))
        story.append(Paragraph(f"Flat: {flat_id} | Date: {report_date}", styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))

        # Summary Section
        story.append(Paragraph("📊 Summary", heading_style))
        summary_data = [
            ["Metric", "Value"],
            ["Total Water Used", f"{report['total_usage_ml']:.2f} ml"],
            ["Water Left (Minimum)", f"{report['min_water_left_ml']:.2f} ml"],
            ["Average Flow Rate", f"{report['average_flow_ml_min']:.2f} ml/min"],
            ["Peak Flow Rate", f"{report['peak_flow_ml_min']:.2f} ml/min"],
            ["Peak Usage Time", report["peak_usage_timestamp"]],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 3 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 0.2 * inch))

        # Insights Section
        story.append(Paragraph("💡 Insights & Recommendations", heading_style))
        story.append(Paragraph(report["suggested_reduction"], styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))

        # Footer
        story.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ParagraphStyle(
                    "Footer",
                    parent=styles["Normal"],
                    fontSize=9,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                ),
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_weekly_report_pdf(
        reports: List[Dict[str, Any]], flat_id: str = "flat_001"
    ) -> bytes:
        """
        Generate a PDF for weekly summary.

        Args:
            reports: List of daily report dictionaries
            flat_id: Flat identifier

        Returns:
            PDF as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#2ca02c"),
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#333333"),
            spaceAfter=6,
        )

        # Title
        story.append(Paragraph(f"💧 Weekly Water Usage Report", title_style))
        story.append(
            Paragraph(f"Flat: {flat_id} | Period: Last 7 Days", styles["Normal"])
        )
        story.append(Spacer(1, 0.3 * inch))

        # Weekly Summary
        if reports:
            total_usage = sum(r["total_usage_ml"] for r in reports)
            avg_daily_usage = total_usage / len(reports) if reports else 0
            peak_flow = max(r["peak_flow_ml_min"] for r in reports)
            min_water = min(r["min_water_left_ml"] for r in reports)

            story.append(Paragraph("📈 Weekly Summary", heading_style))
            weekly_data = [
                ["Metric", "Value"],
                ["Total Water Used (7 days)", f"{total_usage:.2f} ml"],
                ["Average Daily Usage", f"{avg_daily_usage:.2f} ml"],
                ["Peak Flow Rate (Week)", f"{peak_flow:.2f} ml/min"],
                ["Minimum Water Level", f"{min_water:.2f} ml"],
                ["Number of Reports", f"{len(reports)}"],
            ]

            weekly_table = Table(weekly_data, colWidths=[3 * inch, 3 * inch])
            weekly_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ca02c")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgreen),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            story.append(weekly_table)
            story.append(Spacer(1, 0.3 * inch))

            # Daily breakdown
            story.append(Paragraph("📅 Daily Breakdown", heading_style))
            daily_data = [["Date", "Total Usage (ml)", "Peak Flow (ml/min)", "Status"]]

            for report in reports:
                date = datetime.fromisoformat(report["report_timestamp"]).strftime(
                    "%Y-%m-%d"
                )
                usage = report["total_usage_ml"]
                peak = report["peak_flow_ml_min"]
                status = PDFReportGenerator._get_status(usage)

                daily_data.append([date, f"{usage:.2f}", f"{peak:.2f}", status])

            daily_table = Table(daily_data, colWidths=[1.5 * inch, 2 * inch, 2 * inch, 1.5 * inch])
            daily_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ca02c")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            story.append(daily_table)

        story.append(Spacer(1, 0.3 * inch))
        story.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ParagraphStyle(
                    "Footer",
                    parent=styles["Normal"],
                    fontSize=9,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                ),
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def _get_status(usage_ml: float, threshold: float = 2500) -> str:
        """Get status label for usage."""
        if usage_ml <= threshold * 0.7:
            return "✅ Efficient"
        elif usage_ml <= threshold:
            return "⚪ Normal"
        elif usage_ml <= threshold * 1.2:
            return "⚠️ High"
        else:
            return "❌ Penalty"
