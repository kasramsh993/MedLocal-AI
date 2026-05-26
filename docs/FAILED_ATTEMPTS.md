# Failed attempts and retired approaches

**Purpose:** Record what we tried, why it did not stick, and what to do instead — so Cursor, Codex, and future-you do not repeat the same work.

**Last updated:** 2026-05-26

---

## How to log an entry

Copy this template for each attempt:

```markdown
## YYYY-MM-DD — Short title

**Goal:** What we wanted to achieve

**What we tried:** Files, approach, prompts, models

**Outcome:** Failed / partial / reverted

**Why it failed:** Root cause

**Lesson / do instead:** Concrete guidance
```

---

## 2026-05-26 — Letter-style Ollama prompt path (`templates/prompts.py`)

**Goal:** Generate a full Arztbrief directly from the LLM with tone and specialty instructions (`build_system_prompt` / `build_user_prompt`).

**What we tried:** Prompt templates in `templates/prompts.py` and context assembly in `generation/context_builder.py`; fallback letter in `generation/fallback_report.py`.

**Outcome:** Superseded in live `app.py` flow — generation now asks Ollama for **strict JSON** clinical sections, then renders via `report_renderer` + `final_report_guard`.

**Why it changed:** JSON extraction + deterministic rendering gives more consistent insurer-ready structure and fewer prompt artifacts in the final letter.

**Lesson / do instead:** Extend the JSON schema + renderer path; do not reintroduce long free-form letter prompts without re-validating guard rules. Remove dead imports when cleaning (see [NEXT_STEPS.md](NEXT_STEPS.md)).

---

## 2026-05-26 — Duplicate report cleaning (`utils/report_cleaning.py`)

**Goal:** Strip internal prompt lines and duplicate headings from model output.

**What we tried:** `clean_final_report_text()` in `utils/report_cleaning.py`.

**Outcome:** Unused; `validation/final_report_guard.py` (`sanitize_and_validate_final_report`) is what `app.py` calls.

**Why:** Two similar implementations diverged during PoC iteration.

**Lesson / do instead:** Consolidate into one module; delete `report_cleaning.py` after merge.

---

## 2026-05-26 — Legacy code suggestions (`utils/medical_codes.py`)

**Goal:** Simple specialty-based ICD/GOÄ hints from note keywords.

**What we tried:** `suggest_codes()` and `split_code_suggestions()`.

**Outcome:** Replaced by `coding/icd10_search.py` and `billing/billing_optimizer.py` with mock JSON corpora. Only `SPECIALTY_ICONS` remains in use.

**Lesson / do instead:** Extend ICD/billing modules; do not revive `suggest_codes` without a clear reason.

---

## Placeholder for ML / model experiments

When you try a larger Ollama model, fine-tuning, or a different extraction format and it fails, add an entry here (model name, hardware limits, quality issues, regression in validation scripts).
