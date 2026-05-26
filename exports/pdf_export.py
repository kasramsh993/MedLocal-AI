from __future__ import annotations

import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

from validation.final_report_guard import sanitize_and_validate_final_report


BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = BASE_DIR / "exports" / "reports"
REPORT_SECTION_HEADERS = {
    "Ärztliche Stellungnahme zur Vorlage bei der Krankenversicherung",
    "Praxisdaten",
    "Patienten- und Versicherungsdaten",
    "Betreff",
    "Anlass der Vorstellung",
    "Anamnese",
    "Untersuchungsbefund",
    "Diagnostische Einschätzung / Diagnosen",
    "Diagnosen",
    "Durchgeführte ärztliche Leistungen",
    "Therapie / Empfehlung",
    "Medizinische Begründung",
    "Abrechnungshinweise",
    "Hinweis",
    "Ort, Datum",
    "Ärztliche Unterschrift / Praxisstempel",
}


def sanitize_filename(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9ÄÖÜäöüß_-]+", "_", value.strip())
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean or "patient"


def build_pdf_file_name(report_data: dict[str, Any]) -> str:
    patient = sanitize_filename(report_data.get("patient_name", "patient"))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"arztbrief_{patient}_{stamp}.pdf"


def build_report_pdf_bytes(report_data: dict[str, Any]) -> bytes:
    language = report_data.get("language", "de")
    final_report, _ = sanitize_and_validate_final_report(report_data.get("final_report", ""), language=language)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42,
        title="MedLocal AI Arztbrief",
    )
    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    body.leading = 14

    escaped = _format_report_for_pdf(final_report)
    doc.build([Paragraph(escaped, body)])
    return buffer.getvalue()


def export_report_to_pdf(report_data: dict[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = REPORT_DIR / build_pdf_file_name(report_data)
    pdf_path.write_bytes(build_report_pdf_bytes(report_data))
    return pdf_path


def _escape_pdf_text(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _format_report_for_pdf(report: str) -> str:
    lines = []
    for line in str(report or "").splitlines():
        stripped = line.strip()
        escaped = _escape_pdf_text(stripped if stripped else line)
        if stripped in REPORT_SECTION_HEADERS or stripped.startswith("An die zuständige Krankenversicherung"):
            lines.append(f"<b>{escaped}</b>")
        else:
            lines.append(escaped)
    return "<br/>".join(lines)
