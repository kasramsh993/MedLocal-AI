from __future__ import annotations


def build_generation_context(
    patient: dict,
    specialty: str,
    insurance_type: str,
    approved_transcript: str,
    additional_notes: str,
    language: str,
    tone: str,
    icd10_suggestions: list[dict] | None = None,
    billing_suggestions: list[dict] | None = None,
) -> str:
    missing = "Not provided" if language == "en" else "Nicht angegeben"

    def value(key: str) -> str:
        raw = str(patient.get(key, "") or "").strip()
        return raw if raw and raw != "-" else missing

    tone_labels = {
        "short_concise": "Short & Concise" if language == "en" else "Kurz & Prägnant",
        "detailed": "Detailed" if language == "en" else "Detailliert",
        "patient_friendly": "Patient Friendly" if language == "en" else "Patientenfreundlich",
    }

    def list_codes(items: list[dict] | None) -> str:
        if not items:
            return missing
        rows = []
        for item in items:
            system = str(item.get("system", "") or "").strip()
            label = item.get("label") or item.get("label_de") or item.get("label_en") or ""
            why = item.get("why") or ", ".join(item.get("matched_terms", []))
            prefix = f"{system} " if system else ""
            rows.append(f"- {prefix}{item.get('code', '')}: {label} ({why})".strip())
        return "\n".join(rows)

    return "\n".join(
        [
            "Purpose: insurance-company-ready medical report for submission to the patient's insurer.",
            f"Output language: {'English' if language == 'en' else 'Deutsch'}",
            f"Specialty / Fachrichtung: {specialty}",
            f"Tone of voice: {tone_labels.get(tone, tone)} ({tone})",
            f"Insurance type / Versicherungsart: {insurance_type}",
            f"Insurer / Kostenträger: {value('insurance_provider')}",
            f"Insurance or policy number: {value('insurance_number')}",
            "",
            "Patient metadata:",
            f"Name: {value('name')}",
            f"Date of birth / Geburtsdatum: {value('dob')}",
            f"Address / Adresse: {value('address')}",
            f"Treatment date / Behandlungsdatum: {value('visit_date')}",
            f"Treating physician / Behandelnder Arzt: {value('doctor_name')}",
            "",
            "Transcript / Transkript:",
            approved_transcript.strip() or missing,
            "",
            "Additional clinical notes / zusätzliche klinische Notizen:",
            additional_notes.strip() or missing,
            "",
            "Local ICD-10-GM suggestions:",
            list_codes(icd10_suggestions),
            "",
            "Billing suggestions with documented action evidence only:",
            list_codes(billing_suggestions),
        ]
    )
