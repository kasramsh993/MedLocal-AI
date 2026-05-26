from __future__ import annotations


SPECIALTY_MULTIPLIERS = {
    "Allgemeinmedizin": 1.1,
    "Urologie": 1.2,
    "Orthopädie": 1.2,
    "OrthopÃ¤die": 1.2,
    "Kardiologie": 1.3,
    "Dermatologie": 1.0,
    "Zahnmedizin": 1.0,
}


def format_duration(seconds: int | float | None, language: str = "de") -> str:
    total = max(0, int(round(seconds or 0)))
    minutes, rest = divmod(total, 60)
    if language == "en":
        return f"{minutes}m {rest}s" if minutes else f"{rest}s"
    return f"{minutes} Min. {rest} Sek." if minutes else f"{rest} Sek."


def estimate_manual_documentation_time(
    transcript_text: str,
    clinical_notes: str,
    generated_report: str,
    specialty: str,
    document_type: str = "arztbrief",
    includes_icd: bool = True,
    includes_billing: bool = False,
    ai_workflow_sec: int | float = 0,
    language: str = "de",
) -> dict:
    report_words = len((generated_report or "").split())
    transcript_words = len((transcript_text or "").split())
    notes_words = len((clinical_notes or "").split())

    base_manual_sec = 600 if document_type == "arztbrief" else 480
    report_length_sec = report_words * 1.0
    transcript_review_sec = (transcript_words + notes_words) * 0.3
    icd_lookup_sec = 90 if includes_icd else 0
    billing_review_sec = 180 if includes_billing else 0
    insurance_complexity_sec = 90
    multiplier = SPECIALTY_MULTIPLIERS.get(specialty, 1.1)

    manual_estimate_sec = int(
        (
            base_manual_sec
            + report_length_sec
            + transcript_review_sec
            + icd_lookup_sec
            + billing_review_sec
            + insurance_complexity_sec
        )
        * multiplier
    )
    ai_workflow_sec = int(round(ai_workflow_sec or 0))
    estimated_saved_sec = max(0, manual_estimate_sec - ai_workflow_sec)

    if language == "en":
        assumptions = [
            "Demo estimate: calculated conservatively for a full manual medical letter, ICD coding and billing-review workflow.",
            "Base manual medical-letter time: 10 minutes",
            f"Report length factor: {report_words} words × 1.0 seconds",
            f"Transcript and notes review factor: {transcript_words + notes_words} words × 0.3 seconds",
            "ICD-10-GM lookup time: 90 seconds" if includes_icd else "No ICD-10-GM lookup time included",
            "Billing-review time: 180 seconds" if includes_billing else "No billing-review time included",
            "Insurance documentation complexity: 90 seconds",
            f"Specialty multiplier: {multiplier}",
            "Measured AI workflow time is subtracted from the manual estimate",
        ]
    else:
        assumptions = [
            "Demo-Schätzung: konservativ zugunsten eines vollständigen manuellen Arztbrief-, ICD- und Abrechnungsworkflows kalkuliert.",
            "Basiszeit für manuellen Arztbrief: 10 Minuten",
            f"Dokumentlängenfaktor: {report_words} Wörter × 1,0 Sekunden",
            f"Transkript- und Notizprüfung: {transcript_words + notes_words} Wörter × 0,3 Sekunden",
            "ICD-10-GM-Recherche: 90 Sekunden" if includes_icd else "Keine ICD-10-GM-Recherche eingerechnet",
            "Abrechnungsprüfung: 180 Sekunden" if includes_billing else "Keine Abrechnungsprüfung eingerechnet",
            "Versicherungsbezogene Dokumentationskomplexität: 90 Sekunden",
            f"Fachrichtungsfaktor: {multiplier}",
            "Gemessene KI-Workflow-Zeit wird von der manuellen Schätzung abgezogen",
        ]

    return {
        "manual_estimate_sec": manual_estimate_sec,
        "ai_workflow_sec": ai_workflow_sec,
        "estimated_saved_sec": estimated_saved_sec,
        "method": "demo_manual_documentation_minus_measured_ai_workflow",
        "assumptions": assumptions,
    }
