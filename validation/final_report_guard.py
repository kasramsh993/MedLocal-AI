from __future__ import annotations

import re

from utils.text_cleaning import clean_transcript_text


FORBIDDEN_STRINGS = [
    "<br",
    "Purpose:",
    "Output language:",
    "Patient metadata",
    "Klinischer Kontext",
    "Specialty / Fachrichtung",
    "| Patientname |",
    "{{",
    "[Patient",
    "###",
    "kaltgeworden",
    "Die Partien",
]

GERMAN_FORBIDDEN_LABELS = [
    "Practice header",
    "Patient data",
    "Insurance data",
    "Treatment date",
    "Output language",
    "Clinical context",
]

# Lines that look like leaked prompt / context scaffolding (prefix match, silent drop).
CONTEXT_LINE_PREFIXES = (
    "Purpose:",
    "Output language:",
    "Specialty / Fachrichtung:",
    "Insurance type / Versicherungsart:",
    "Patient metadata",
    "Clinical context:",
    "Klinischer Kontext",
)


def sanitize_and_validate_final_report(report_text: str, language: str = "de") -> tuple[str, list[str]]:
    text = clean_transcript_text(report_text)
    warnings: list[str] = []
    lines: list[str] = []
    seen_headings: set[str] = set()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if any(line.startswith(prefix) for prefix in CONTEXT_LINE_PREFIXES):
            continue
        if re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$", line):
            warnings.append("Removed markdown table separator")
            continue
        if any(marker.lower() in line.lower() for marker in FORBIDDEN_STRINGS):
            warnings.append(f"Removed forbidden artifact: {line[:40]}")
            continue
        if language == "de" and any(label.lower() in line.lower() for label in GERMAN_FORBIDDEN_LABELS):
            warnings.append(f"Removed English label: {line[:40]}")
            continue
        if re.match(r"^\|.*\|$", line):
            warnings.append("Removed markdown table line")
            continue
        key = line.rstrip(":").lower()
        if key in {
            "praxisbriefkopf",
            "praxisdaten",
            "patientendaten",
            "patienten- und versicherungsdaten",
            "versicherungsdaten",
            "behandlungsdatum",
            "empfänger",
            "empfaenger",
        }:
            if key in seen_headings:
                warnings.append(f"Removed duplicate heading: {line}")
                continue
            seen_headings.add(key)
        lines.append(line)

    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    if any(marker.lower() in cleaned.lower() for marker in FORBIDDEN_STRINGS):
        warnings.append("Forbidden artifact remains")
    if language == "de" and any(label.lower() in cleaned.lower() for label in GERMAN_FORBIDDEN_LABELS):
        warnings.append("English label remains in German report")
    if re.search(r"\[[A-Za-z0-9_ -]{3,}\]|\{\{.*?\}\}", cleaned):
        warnings.append("Unresolved placeholder remains")
    return cleaned, warnings
