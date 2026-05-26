from __future__ import annotations

from typing import Any


REPORT_FIELDS = [
    "recipient",
    "practice_header",
    "patient_name",
    "patient_dob",
    "patient_address",
    "insurance_type",
    "insurer",
    "treatment_date",
    "treating_physician",
    "specialty",
    "subject",
    "reason_for_visit",
    "history",
    "findings",
    "assessment",
    "diagnoses",
    "services_performed",
    "therapy_recommendation",
    "medical_justification",
    "billing_notes",
    "disclaimer",
    "closing",
    "signature",
]


def missing_value(language: str = "de") -> str:
    return "Not provided" if language == "en" else "Nicht angegeben"


def safe_value(value: Any, language: str = "de") -> str:
    text = str(value or "").strip()
    if text and text != "-":
        return text
    return missing_value(language)


def build_report_object(
    patient: dict,
    specialty: str,
    insurance_type: str,
    clinical_sections: dict,
    language: str = "de",
) -> dict:
    insurer = safe_value(patient.get("insurance_provider"), language)
    if language == "en":
        recipient = f"To the responsible insurance provider ({insurer})" if insurer != "Not provided" else "To the responsible insurance provider"
        subject = "Medical statement / treatment report for submission to the insurance provider"
        disclaimer = "This report is intended as medical documentation for submission to the insurance provider."
        closing = "Sincerely"
        signature = "Physician signature / practice stamp"
        practice_header = "Practice data"
    else:
        recipient = f"An die zuständige Krankenversicherung ({insurer})" if insurer != "Nicht angegeben" else "An die zuständige Krankenversicherung"
        subject = "Ärztliche Stellungnahme / Behandlungsbericht zur Vorlage bei der Krankenversicherung"
        disclaimer = "Dieser Bericht dient der medizinischen Dokumentation zur Vorlage bei der Krankenversicherung."
        closing = "Mit freundlichen Grüßen"
        signature = "Ärztliche Unterschrift / Praxisstempel"
        practice_header = "Praxisdaten"

    diagnoses = clinical_sections.get("diagnoses") or []
    services = clinical_sections.get("services_performed") or []
    if isinstance(diagnoses, str):
        diagnoses = [diagnoses]
    if isinstance(services, str):
        services = [services]

    return {
        "recipient": recipient,
        "practice_header": practice_header,
        "patient_name": safe_value(patient.get("name"), language),
        "patient_dob": safe_value(patient.get("dob"), language),
        "patient_address": safe_value(patient.get("address"), language),
        "insurance_type": safe_value(insurance_type or patient.get("insurance_type"), language),
        "insurer": insurer,
        "treatment_date": safe_value(patient.get("visit_date"), language),
        "treating_physician": safe_value(patient.get("doctor_name"), language),
        "specialty": safe_value(specialty, language),
        "subject": subject,
        "reason_for_visit": safe_value(clinical_sections.get("reason_for_visit"), language),
        "history": safe_value(clinical_sections.get("history"), language),
        "findings": safe_value(clinical_sections.get("findings"), language),
        "assessment": safe_value(clinical_sections.get("assessment"), language),
        "diagnoses": [safe_value(item, language) for item in diagnoses if str(item or "").strip()] or [missing_value(language)],
        "services_performed": [safe_value(item, language) for item in services if str(item or "").strip()] or [missing_value(language)],
        "therapy_recommendation": safe_value(clinical_sections.get("therapy_recommendation"), language),
        "medical_justification": safe_value(clinical_sections.get("medical_justification"), language),
        "billing_notes": safe_value(clinical_sections.get("billing_notes"), language),
        "disclaimer": disclaimer,
        "closing": closing,
        "signature": signature,
    }
