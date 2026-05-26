SPECIALTY_ICONS = {
    "Allgemeinmedizin": "AM",
    "Urologie": "UR",
    "Zahnmedizin": "ZM",
    "Kardiologie": "KA",
    "Dermatologie": "DE",
    "Orthopädie": "OR",
}


def suggest_codes(specialty: str, notes: str, is_pkv: bool) -> list[dict]:
    text = notes.lower()
    suggestions = []

    if specialty == "Kardiologie" or any(term in text for term in ["ekg", "brustschmerz", "thorax", "hypertonie"]):
        suggestions.extend([
            {"code": "I10.90", "label": "Essentielle Hypertonie, nicht näher bezeichnet", "confidence": "hoch"},
            {"code": "GOÄ 651", "label": "Elektrokardiographische Untersuchung", "confidence": "mittel"},
        ])
    elif specialty == "Dermatologie" or any(term in text for term in ["exanthem", "haut", "dermatitis"]):
        suggestions.extend([
            {"code": "L30.9", "label": "Dermatitis, nicht näher bezeichnet", "confidence": "mittel"},
            {"code": "GOÄ 750", "label": "Auflichtmikroskopische Untersuchung", "confidence": "niedrig"},
        ])
    elif specialty == "Orthopädie" or any(term in text for term in ["rücken", "knie", "schulter"]):
        suggestions.extend([
            {"code": "M54.5", "label": "Kreuzschmerz", "confidence": "mittel"},
            {"code": "GOÄ 7", "label": "Vollständige körperliche Untersuchung", "confidence": "mittel"},
        ])
    elif specialty == "Zahnmedizin":
        suggestions.extend([
            {"code": "K02.9", "label": "Zahnkaries, nicht näher bezeichnet", "confidence": "mittel"},
            {"code": "GOZ 0010", "label": "Eingehende Untersuchung", "confidence": "hoch"},
        ])
    elif specialty == "Urologie":
        suggestions.extend([
            {"code": "N39.0", "label": "Harnwegsinfektion, Lokalisation nicht näher bezeichnet", "confidence": "mittel"},
            {"code": "GOÄ 410", "label": "Ultraschalluntersuchung eines Organs", "confidence": "niedrig"},
        ])
    else:
        suggestions.extend([
            {"code": "Z00.0", "label": "Allgemeinuntersuchung", "confidence": "mittel"},
            {"code": "GOÄ 5", "label": "Symptombezogene Untersuchung", "confidence": "hoch" if is_pkv else "mittel"},
        ])

    return suggestions[:4]


def split_code_suggestions(suggestions: list[dict]) -> tuple[list[dict], list[dict]]:
    icd10 = [item for item in suggestions if not item["code"].startswith(("GOÄ", "GOZ"))]
    billing = [item for item in suggestions if item["code"].startswith(("GOÄ", "GOZ"))]
    return icd10, billing
