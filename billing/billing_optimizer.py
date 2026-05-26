import json
from functools import lru_cache
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "billing" / "billing_codes_mock.json"


BILLABLE_ACTION_TERMS = {
    "de": {
        "Beratung": ["beratung", "gespräch", "ausführliches gespräch", "therapieplanung", "aufklärung"],
        "Untersuchung": ["untersuchung", "körperliche untersuchung", "befund erhoben", "auskultation"],
        "EKG": ["ekg", "ruhe-ekg", "belastungs-ekg"],
        "Sonographie": ["ultraschall", "sonographie", "restharn"],
        "Labor": ["labor", "blutentnahme", "hba1c", "lipide"],
        "Injektion": ["injektion", "impfung", "spritze"],
        "Verband": ["verband", "wundversorgung", "wunde versorgt"],
        "AU": ["au", "arbeitsunfähigkeit", "krankschreibung"],
        "Medikamentenanpassung": ["medikamentenanpassung", "medikation angepasst", "dosis angepasst"],
        "Überweisung": ["überweisung", "überwiesen", "facharzt empfohlen"],
        "Verlaufskontrolle": ["verlaufskontrolle", "kontrolle", "wiedervorstellung", "follow-up"],
        "Dauer dokumentiert": ["minuten", "dauer", "15 min", "20 min", "30 min"],
    },
    "en": {
        "Consultation": ["consultation", "counseling", "therapy planning"],
        "Examination": ["examination", "physical exam", "findings obtained"],
        "ECG": ["ecg", "ekg"],
        "Ultrasound": ["ultrasound", "sonography"],
        "Laboratory": ["lab", "blood draw", "hba1c", "lipids"],
        "Injection": ["injection", "vaccination"],
        "Dressing": ["dressing", "wound care"],
        "Sick note": ["sick note", "incapacity for work"],
        "Medication adjustment": ["medication adjustment", "dose adjusted"],
        "Referral": ["referral", "referred"],
        "Follow-up planning": ["follow-up", "review planned"],
        "Duration documented": ["minutes", "duration", "15 min", "20 min", "30 min"],
    },
}


@lru_cache(maxsize=1)
def load_billing_codes() -> list[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def detect_clinical_actions(text: str, language: str = "de") -> list[str]:
    query = (text or "").lower()
    actions = []
    for label, terms in BILLABLE_ACTION_TERMS.get(language, BILLABLE_ACTION_TERMS["de"]).items():
        if any(term in query for term in terms):
            actions.append(label)
    return actions


def has_billable_action_evidence(text: str, language: str = "de") -> bool:
    return bool(detect_clinical_actions(text, language))


def suggest_billing_codes(text: str, insurance_type: str, specialty: str, language: str = "de", limit: int = 8) -> list[dict]:
    query = (text or "").lower()
    if not query.strip() or not has_billable_action_evidence(query, language):
        return []

    target = _target_system(insurance_type)
    scored = []
    action_terms = {
        term
        for terms in BILLABLE_ACTION_TERMS.get(language, BILLABLE_ACTION_TERMS["de"]).values()
        for term in terms
        if term in query
    }

    for item in load_billing_codes():
        if target and item["system"] != target:
            continue
        if specialty not in item.get("specialties", []) and "Allgemeinmedizin" not in item.get("specialties", []):
            continue
        keywords = item.get("keywords_en" if language == "en" else "keywords_de", [])
        score = 0
        matched = []
        for keyword in keywords:
            key = keyword.lower()
            if key in query and (key in action_terms or any(action in key or key in action for action in action_terms)):
                score += 4
                matched.append(keyword)
        if not matched:
            continue
        if specialty in item.get("specialties", []):
            score += 1
        row = dict(item)
        row["score"] = score
        row["matched_terms"] = matched[:4]
        scored.append(row)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def format_billing_suggestions(suggestions: list[dict], language: str = "de") -> list[dict]:
    label_key = "label_en" if language == "en" else "label_de"
    req_key = "documentation_requirements_en" if language == "en" else "documentation_requirements_de"
    warning_key = "warning_en" if language == "en" else "warning_de"
    return [
        {
            "system": item["system"],
            "code": item["code"],
            "label": item.get(label_key, item.get("label_de", "")),
            "why": ", ".join(item.get("matched_terms", [])),
            "documentation_requirements": item.get(req_key, []),
            "warning": item.get(warning_key, ""),
            "estimated_eur_min": item.get("estimated_eur_min"),
            "estimated_eur_max": item.get("estimated_eur_max"),
            "points": item.get("points"),
            "goae_factor_default": item.get("goae_factor_default"),
            "value_note": item.get("value_note_en" if language == "en" else "value_note_de", ""),
        }
        for item in suggestions
    ]


def calculate_billing_potential(suggestions: list[dict], language: str = "de") -> dict:
    seen: set[tuple[str, str]] = set()
    items = []
    total_min = 0.0
    total_max = 0.0

    for item in suggestions:
        key = (str(item.get("system", "")), str(item.get("code", "")))
        if key in seen:
            continue
        seen.add(key)
        min_value = item.get("estimated_eur_min")
        max_value = item.get("estimated_eur_max")
        if min_value is None or max_value is None:
            continue
        min_float = float(min_value)
        max_float = float(max_value)
        total_min += min_float
        total_max += max_float
        row = dict(item)
        row["estimated_eur_min"] = min_float
        row["estimated_eur_max"] = max_float
        row["display_amount"] = _format_eur_range(min_float, max_float, language)
        items.append(row)

    return {
        "items": items,
        "total_min": round(total_min, 2),
        "total_max": round(total_max, 2),
        "display_total": _format_eur_range(total_min, total_max, language),
    }


def _format_eur_range(min_value: float, max_value: float, language: str) -> str:
    if min_value == 0 and max_value == 0:
        return "€0.00" if language == "en" else "0,00 €"
    if language == "en":
        return f"€{min_value:,.2f}–€{max_value:,.2f}" if min_value != max_value else f"€{min_value:,.2f}"
    min_text = f"{min_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    max_text = f"{max_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{min_text}–{max_text} €" if min_value != max_value else f"{min_text} €"


def _target_system(insurance_type: str) -> str | None:
    if insurance_type == "GKV":
        return "EBM"
    if insurance_type in {"Privat (PKV)", "Selbstzahler"}:
        return "GOÄ"
    return None
