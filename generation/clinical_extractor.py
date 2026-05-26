from __future__ import annotations

import json
import re
from typing import Any

from utils.text_cleaning import clean_transcript_text


EXPECTED_KEYS = {
    "reason_for_visit",
    "history",
    "findings",
    "assessment",
    "diagnoses",
    "services_performed",
    "therapy_recommendation",
    "medical_justification",
    "billing_notes",
}


def extract_clinical_sections(input_text: str, metadata: dict | None = None, language: str = "de", model_output: str | None = None) -> dict:
    parsed = _parse_json_sections(model_output or "", language)
    if parsed:
        return parsed
    return _fallback_extract(input_text, language)


def _parse_json_sections(output: str, language: str) -> dict | None:
    text = (output or "").strip()
    if not text:
        return None
    forbidden = [
        "Purpose:",
        "Output language:",
        "Patient metadata",
        "Klinischer Kontext",
        "Specialty / Fachrichtung",
        "kaltgeworden",
        "Die Partien",
    ]
    if any(marker.lower() in text.lower() for marker in forbidden):
        return None
    if "<" in text or "|" in text or "###" in text:
        return None
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or not EXPECTED_KEYS.intersection(data):
        return None
    return _normalize_sections(data, language)


def _normalize_sections(data: dict[str, Any], language: str) -> dict:
    fallback = _fallback_extract("", language)
    normalized = {}
    for key in EXPECTED_KEYS:
        value = data.get(key)
        if key in {"diagnoses", "services_performed"}:
            if isinstance(value, list):
                normalized[key] = [clean_transcript_text(str(item)) for item in value if str(item or "").strip()]
            elif value:
                normalized[key] = [clean_transcript_text(str(value))]
            else:
                normalized[key] = fallback[key]
        else:
            normalized[key] = clean_transcript_text(str(value or "")) or fallback[key]
    return normalized


def _fallback_extract(input_text: str, language: str = "de") -> dict:
    text = clean_transcript_text(input_text)
    lowered = text.lower()
    cold = any(term in lowered for term in ["erkältung", "erkaeltung", "husten", "schnupfen", "infekt", "cold", "cough"])
    fever = any(term in lowered for term in ["fieber", "fever"])
    no_fever = any(term in lowered for term in ["kein fieber", "ohne fieber", "no fever"])
    ekg = "ekg" in lowered
    exam = any(term in lowered for term in ["untersuchung", "untersucht", "körperliche", "koerperliche", "examination"])

    if language == "en":
        complaint = "cold-like symptoms" if cold else "the documented symptoms"
        diagnosis = "Suspected acute upper respiratory tract infection" if cold else "Clinical assessment based on the documented information"
        findings = "No further examination findings were documented."
        if no_fever:
            findings = "No fever was documented. Further examination findings were not documented."
        elif fever:
            findings = "Fever was documented. Further examination findings were not documented."
        services = ["Medical consultation / presentation"]
        if exam:
            services.append("Medical examination, as documented")
        if ekg:
            services.append("ECG, as documented")
        return {
            "reason_for_visit": f"Presentation due to {complaint}.",
            "history": f"The patient reports symptoms consistent with {complaint}." if cold else f"The patient presented with the following documented information: {text or 'Not provided'}.",
            "findings": findings,
            "assessment": diagnosis + ".",
            "diagnoses": [diagnosis],
            "services_performed": services,
            "therapy_recommendation": "Symptomatic treatment and follow-up if symptoms persist or worsen.",
            "medical_justification": "Medical documentation is provided based on the stated symptoms and for submission to the insurance provider.",
            "billing_notes": "No additional billable services are sufficiently documented.",
        }

    diagnosis = "Verdacht auf akuten Infekt der oberen Atemwege" if cold else "Klinische Einschätzung auf Grundlage der dokumentierten Angaben"
    findings = "Weitere Untersuchungsbefunde wurden nicht dokumentiert."
    if no_fever:
        findings = "Kein Fieber dokumentiert. Weitere Untersuchungsbefunde wurden nicht dokumentiert."
    elif fever:
        findings = "Fieber wurde dokumentiert. Weitere Untersuchungsbefunde wurden nicht dokumentiert."
    services = ["Ärztliche Beratung / Vorstellung"]
    if exam:
        services.append("Ärztliche Untersuchung, soweit dokumentiert")
    if ekg:
        services.append("EKG, soweit dokumentiert")

    return {
        "reason_for_visit": "Vorstellung wegen erkältungsähnlicher Beschwerden." if cold else "Vorstellung wegen dokumentierter Beschwerden.",
        "history": "Der Patient berichtet über erkältungsähnliche Beschwerden im Sinne einer Erkältung." if cold else f"Dokumentiert wurde: {text or 'Nicht angegeben'}.",
        "findings": findings,
        "assessment": diagnosis + ".",
        "diagnoses": [diagnosis],
        "services_performed": services,
        "therapy_recommendation": "Symptomatische Behandlung und Verlaufskontrolle bei Persistenz oder Verschlechterung der Beschwerden.",
        "medical_justification": "Die medizinische Dokumentation erfolgt aufgrund der angegebenen Beschwerden und zur Vorlage bei der Krankenversicherung.",
        "billing_notes": "Keine zusätzlichen abrechnungsrelevanten Leistungen ausreichend dokumentiert.",
    }
