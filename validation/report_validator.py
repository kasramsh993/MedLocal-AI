from __future__ import annotations

import re
from typing import Any


PLACEHOLDER_PATTERNS = [
    r"\[[A-Za-z0-9_ -]{3,}\]",
    r"\{\{.*?\}\}",
    r"\bPatientID\b",
    r"\bPatientName\b",
    r"\bPatientAge\b",
    r"\bPatientGender\b",
    r"\bPatientBirthDay\b",
    r"\bTODO\b",
    r"\bLorem ipsum\b",
]

INTERNAL_ARTIFACTS = [
    "Purpose:",
    "Output language:",
    "Specialty / Fachrichtung:",
    "Insurance type / Versicherungsart:",
    "Patient metadata",
    "Klinischer Kontext",
    "Clinical context:",
    "Transkript",
    "Approved transcript",
    "Additional clinical notes",
    "{{",
    "[Patient",
    "TODO",
    "<br",
    "###",
    "| Patientname |",
]


SECTION_CHECKS = {
    "de": {
        "Empfänger / Krankenversicherung": ["krankenversicherung", "empfänger", "kostenträger"],
        "Diagnosen": ["diagnos"],
        "Untersuchungsbefund": ["befund", "untersuchungsbefund"],
        "Medizinische Begründung": ["medizinische begründung", "medizinische notwendigkeit", "medizinische nachvollziehbarkeit", "vorlage bei der krankenversicherung", "beurteilung"],
        "Durchgeführte ärztliche Leistungen": ["durchgeführte", "ärztliche leistungen", "leistungen"],
        "Therapie / Empfehlung": ["therapie", "empfehl"],
        "Weiteres Vorgehen": ["weiteres vorgehen", "kontrolle", "wiedervorstellung", "follow-up"],
        "Unterschrift / Praxisstempel": ["unterschrift", "praxisstempel"],
        "Hinweis zur ärztlichen Prüfung": ["ärztliche prüfung", "aerztliche pruefung", "unterschrift"],
    },
    "en": {
        "Recipient / insurance provider": ["insurance provider", "recipient"],
        "Diagnoses": ["diagnos"],
        "Examination findings": ["finding", "examination"],
        "Medical justification": ["medical justification", "medical necessity"],
        "Performed medical services": ["performed medical services", "services"],
        "Treatment / Recommendation": ["treatment", "recommend"],
        "Follow-up": ["follow-up", "follow up", "review"],
        "Signature / practice stamp": ["signature", "practice stamp"],
        "Medical review notice": ["medical review", "signature"],
    },
}


def _provided(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(text and text not in {"-", "Nicht angegeben", "Not provided"})


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def validate_report(report_text: str | None, patient_metadata: dict[str, Any], language: str = "de") -> dict[str, Any]:
    text = report_text or ""
    lower = text.lower()
    missing: list[str] = []
    artifacts: list[str] = []

    placeholders: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        placeholders.extend(re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL))

    if len(text.strip()) < 280:
        missing.append("Realistic document length")

    if contains_internal_prompt_artifacts(text):
        artifacts.append("Internal prompt/context artifact")

    name = patient_metadata.get("name")
    if _provided(name) and str(name).lower() not in lower:
        missing.append("Patient name")

    dob = patient_metadata.get("dob")
    if _provided(dob) and str(dob).lower() not in lower:
        missing.append("Date of birth")

    visit_date = patient_metadata.get("visit_date")
    if _provided(visit_date) and str(visit_date).lower() not in lower:
        missing.append("Treatment date")

    insurance_provider = patient_metadata.get("insurance_provider")
    insurance_type = patient_metadata.get("insurance_type")
    if _provided(insurance_provider) and str(insurance_provider).lower() not in lower:
        missing.append("Insurance data")
    elif _provided(insurance_type) and str(insurance_type).lower() not in lower:
        missing.append("Insurance data")

    for section, markers in SECTION_CHECKS.get(language, SECTION_CHECKS["de"]).items():
        if not _contains_any(lower, markers):
            missing.append(section)

    for marker in ["n/a", "template", "sample only"]:
        if marker in lower:
            artifacts.append(marker)

    # A single dash as a value is acceptable only when no UI metadata exists.
    if re.search(r":\s*-\s*(?:\n|<br|$)", text):
        artifacts.append("Empty dash field")

    return {
        "ok": not missing and not placeholders and not artifacts,
        "missing": missing,
        "placeholders": sorted(set(placeholders)),
        "artifacts": sorted(set(artifacts)),
    }


def contains_internal_prompt_artifacts(report_text: str | None) -> bool:
    text = report_text or ""
    if not text.strip():
        return True
    lower = text.lower()
    if any(marker.lower() in lower for marker in INTERNAL_ARTIFACTS):
        return True
    if re.search(r"^\s*\|.*\|\s*$", text, flags=re.MULTILINE):
        return True
    if lower.count("praxisbriefkopf") > 1 or lower.count("patientendaten") > 1:
        return True
    if re.fullmatch(r"(nicht angegeben\s*)+", lower.strip()):
        return True
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    heading_like = [line for line in lines if line.startswith("#") or len(line.split()) <= 5 and line.endswith(":")]
    if len(lines) >= 6 and len(heading_like) / max(1, len(lines)) > 0.65:
        return True
    if len(text.split()) < 35:
        return True
    return False
