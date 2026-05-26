from __future__ import annotations

import re

from utils.text_cleaning import clean_transcript_text


INTERNAL_CONTEXT_LINES = (
    "Purpose:",
    "Output language:",
    "Specialty / Fachrichtung:",
    "Insurance type / Versicherungsart:",
    "Patient metadata",
    "Clinical context:",
    "Klinischer Kontext",
)


def clean_final_report_text(report_text: str | None) -> str:
    text = clean_transcript_text(report_text or "")
    lines: list[str] = []
    seen_headings: set[str] = set()
    in_table = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            in_table = False
            lines.append("")
            continue
        if any(line.startswith(prefix) for prefix in INTERNAL_CONTEXT_LINES):
            continue
        if re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$", line):
            in_table = True
            continue
        if "|" in line and re.search(r"\b(patient|versicher|geburts|datum|diagnos|befund)\b", line, re.IGNORECASE):
            in_table = True
            line = " ".join(part.strip() for part in line.strip("|").split("|") if part.strip())
        elif in_table and "|" in line:
            line = " ".join(part.strip() for part in line.strip("|").split("|") if part.strip())

        heading_key = line.rstrip(":").lower()
        duplicate_headings = {
            "praxisbriefkopf",
            "patientendaten",
            "versicherungsdaten",
            "behandlungsdatum",
            "empfänger",
            "empfaenger",
        }
        if heading_key in duplicate_headings:
            if heading_key in seen_headings:
                continue
            seen_headings.add(heading_key)
        lines.append(line)

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
