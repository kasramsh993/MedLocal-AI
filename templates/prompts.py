TONE_INSTRUCTIONS = {
    "short_concise": {
        "de": "Formuliere knapp, präzise und ohne unnötige Wiederholungen.",
        "en": "Write concisely, precisely, and without unnecessary repetition.",
    },
    "detailed": {
        "de": "Formuliere ausführlich mit differenzierter medizinischer Einordnung.",
        "en": "Write in a detailed style with differentiated clinical reasoning.",
    },
    "patient_friendly": {
        "de": "Formuliere verständlich und patientennah, ohne medizinische Präzision zu verlieren.",
        "en": "Write clearly and empathetically while preserving medical precision.",
    },
}


def build_system_prompt(is_pkv: bool, specialty: str = "Allgemeinmedizin", tone: str = "short_concise", language: str = "de") -> str:
    tone_text = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["short_concise"])
    if language == "en":
        return (
            "You are a professional medical scribe for a German medical practice. "
            "Draft a formal insurance-company-ready medical report. "
            "Return only the completed report. Do not ask questions. "
            "Use only provided patient, insurance and clinical data. Do not invent undocumented services. "
            "Never leave placeholders such as [PatientName], {{patient}}, TODO or N/A. "
            "If information is missing, write 'Not provided'. "
            "Clearly document medical necessity and performed services only if documented. "
            f"Specialty: {specialty}. {tone_text['en']}"
        )
    return (
        "Du bist ein professioneller medizinischer Schreiber für eine deutsche Arztpraxis. "
        "Erstelle eine formale, versicherungsreife ärztliche Stellungnahme zur Vorlage bei der Krankenversicherung. "
        "Gib ausschließlich den fertigen Bericht aus. Stelle keine Rückfragen. "
        "Verwende nur bereitgestellte Patienten-, Versicherungs- und klinische Daten. "
        "Erfinde keine nicht dokumentierten Leistungen. "
        "Lasse niemals Platzhalter wie [PatientName], {{patient}}, TODO oder N/A stehen. "
        "Wenn Angaben fehlen, schreibe 'Nicht angegeben'. "
        "Dokumentiere medizinische Notwendigkeit und durchgeführte Leistungen nur, wenn sie belegt sind. "
        f"Fachrichtung: {specialty}. {tone_text['de']}"
    )


def build_user_prompt(context: str, is_pkv: bool, language: str = "de") -> str:
    if language == "en":
        return f"""Create an insurance-ready medical report addressed to the responsible insurance provider.

Required structure:
## Practice header
## Recipient
## Patient data
## Insurance data
## Treatment date
## Subject: Medical statement / treatment report for submission to the insurance provider
## Reason for presentation
## History
## Examination findings
## Diagnostic assessment / diagnoses
## Performed medical services
## Treatment / Recommendation
## Medical justification
## Billing-relevant documentation notes
## Notice
## Closing
## Place, date
## Physician signature / practice stamp

Rules:
- Use real metadata from the context and never unresolved placeholders.
- If context is missing, write "Not provided".
- Do not invent services, examinations, billing claims, durations, or diagnoses.
- Billing notes are non-binding assistance and must be checked against EBM/GOÄ rules.
- Include this notice: "This report is intended as medical documentation for submission to the insurance provider."
- Return only the completed report.

Clinical context:
{context}"""

    return f"""Erstelle eine versicherungsreife ärztliche Stellungnahme zur Vorlage bei der Krankenversicherung.

Pflichtstruktur:
## Praxisbriefkopf
## Empfänger
## Patientendaten
## Versicherungsdaten
## Behandlungsdatum
## Betreff: Ärztliche Stellungnahme / Behandlungsbericht zur Vorlage bei der Krankenversicherung
## Anlass der Vorstellung
## Anamnese
## Untersuchungsbefund
## Diagnostische Einschätzung / Diagnosen
## Durchgeführte ärztliche Leistungen
## Therapie / Empfehlung
## Medizinische Begründung
## Abrechnungsrelevante Dokumentationshinweise
## Hinweis
## Schlussformel
## Ort, Datum
## Ärztliche Unterschrift / Praxisstempel

Regeln:
- Verwende echte Metadaten aus dem Kontext und niemals ungelöste Platzhalter.
- Wenn Angaben fehlen, schreibe "Nicht angegeben".
- Erfinde keine Leistungen, Untersuchungen, Abrechnungsansprüche, Zeitdauern oder Diagnosen.
- Abrechnungshinweise sind unverbindlich und anhand der gültigen EBM-/GOÄ-Regeln zu prüfen.
- Füge diesen Hinweis ein: "Dieser Bericht dient der medizinischen Dokumentation zur Vorlage bei der Krankenversicherung."
- Gib ausschließlich den fertigen Bericht aus.

Klinischer Kontext:
{context}"""
