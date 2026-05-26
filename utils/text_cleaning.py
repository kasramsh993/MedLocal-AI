from __future__ import annotations

import re


def clean_transcript_text(text: str | None) -> str:
    """Normalize dictated transcript text without changing medical abbreviations."""
    cleaned = str(text or "")
    cleaned = re.sub(r"<\s*br\s*/?\s*>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"</p\s*>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"^\s{0,3}#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*\|(.+\|)+\s*$", lambda match: match.group(0).replace("|", " "), cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\b(?:Transkript|Transcript)\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
