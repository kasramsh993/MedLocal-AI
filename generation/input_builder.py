from __future__ import annotations

from utils.text_cleaning import clean_transcript_text


def build_normalized_clinical_input(
    approved_transcript: str,
    transcript_draft: str,
    clinical_notes: str,
) -> str:
    transcript = clean_transcript_text(approved_transcript or transcript_draft)
    notes = clean_transcript_text(clinical_notes)
    parts = []
    if transcript:
        parts.append(transcript)
    if notes:
        parts.append(notes)
    return "\n\n".join(parts).strip()
