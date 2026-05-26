from __future__ import annotations

from i18n import t


def validate_generation_input(transcript_text: str, clinical_notes: str, language: str) -> tuple[bool, str]:
    if (transcript_text or "").strip() or (clinical_notes or "").strip():
        return True, ""
    return False, t("generation_input_required", language)
