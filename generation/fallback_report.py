from __future__ import annotations


def build_insurance_ready_fallback_report(context: dict, language: str = "de") -> str:
    patient = context.get("patient", {})
    notes = (context.get("clinical_notes") or context.get("transcript") or "").strip()
    insurer = _value(patient.get("insurance_provider"), language)
    insurance_type = _value(patient.get("insurance_type"), language)
    name = _value(patient.get("name"), language)
    dob = _value(patient.get("dob"), language)
    visit_date = _value(patient.get("visit_date"), language)
    doctor = _value(patient.get("doctor_name"), language)
    diagnosis = _diagnostic_text(notes, language)

    if language == "en":
        return f"""To the responsible insurance provider

Medical statement / treatment report for submission to the insurance provider

Patient:
Name: {name}
Date of birth: {dob}
Insurance: {insurance_type} - {insurer}
Treatment date: {visit_date}

Dear Sir or Madam,

The above-named patient presented with the documented complaint: {notes or "Not provided"}.

Based on the available information, {diagnosis}. Further examination findings were not documented in the clinical notes.

Symptomatic treatment and follow-up in case of persistent or worsening symptoms are recommended.

This report is intended as medical documentation for submission to the insurance provider.

Sincerely,

{doctor}

Place, date

Physician signature / practice stamp"""

    return f"""An die zuständige Krankenversicherung

Ärztliche Stellungnahme / Behandlungsbericht zur Vorlage bei der Krankenversicherung

Patient:
Name: {name}
Geburtsdatum: {dob}
Versicherung: {insurance_type} - {insurer}
Behandlungsdatum: {visit_date}

Sehr geehrte Damen und Herren,

der oben genannte Patient stellte sich mit den dokumentierten Beschwerden vor: {notes or "Nicht angegeben"}.

Auf Grundlage der vorliegenden Angaben besteht {diagnosis}. Weitere Untersuchungsbefunde wurden in den klinischen Notizen nicht dokumentiert.

Eine symptomatische Behandlung sowie Verlaufskontrolle bei Persistenz oder Verschlechterung der Beschwerden wird empfohlen.

Dieser Bericht dient der medizinischen Dokumentation zur Vorlage bei der Krankenversicherung.

Mit freundlichen Grüßen

{doctor}

Ort, Datum

Ärztliche Unterschrift / Praxisstempel"""


def _value(value: object, language: str) -> str:
    text = str(value or "").strip()
    if text and text != "-":
        return text
    return "Not provided" if language == "en" else "Nicht angegeben"


def _diagnostic_text(notes: str, language: str) -> str:
    lowered = notes.lower()
    cold_terms = ["erkältung", "husten", "schnupfen", "infekt", "cold", "cough"]
    if any(term in lowered for term in cold_terms):
        return (
            "there is a suspected acute upper respiratory tract infection"
            if language == "en"
            else "der Verdacht auf einen akuten Infekt der oberen Atemwege"
        )
    return (
        "the clinical assessment is based on the limited documented information"
        if language == "en"
        else "eine klinische Einschätzung auf Basis der begrenzt dokumentierten Angaben"
    )
