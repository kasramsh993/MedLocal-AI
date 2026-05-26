import json
from functools import lru_cache
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "icd10gm" / "icd10gm_mock.json"


@lru_cache(maxsize=1)
def load_icd10gm_codes() -> list[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def search_icd10gm(query_text: str, language: str = "de", limit: int = 5) -> list[dict]:
    query = (query_text or "").lower()
    if not query.strip():
        return []
    label_key = "label_en" if language == "en" else "label_de"
    keywords_key = "keywords_en" if language == "en" else "keywords_de"
    scored = []
    for item in load_icd10gm_codes():
        score = 0
        why = []
        label = item.get(label_key, "").lower()
        if label and label in query:
            score += 5
            why.append(item[label_key])
        for keyword in item.get(keywords_key, []):
            key = keyword.lower()
            if key and key in query:
                score += 3
                why.append(keyword)
        for token in query.split():
            if len(token) >= 5 and token in label:
                score += 1
        if score:
            result = dict(item)
            result["score"] = score
            result["confidence"] = _confidence(score)
            result["matched_terms"] = list(dict.fromkeys(why))[:4]
            result["source"] = "Local ICD-10-GM search"
            scored.append(result)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def format_icd10_suggestions(suggestions: list[dict], language: str = "de") -> list[dict]:
    label_key = "label_en" if language == "en" else "label_de"
    return [
        {
            "code": item["code"],
            "label": item.get(label_key, item.get("label_de", "")),
            "confidence": item.get("confidence", "low"),
            "source": item.get("source", "Local ICD-10-GM search"),
            "matched_terms": item.get("matched_terms", []),
        }
        for item in suggestions
    ]


def _confidence(score: int) -> str:
    if score >= 7:
        return "high"
    if score >= 3:
        return "medium"
    return "low"

