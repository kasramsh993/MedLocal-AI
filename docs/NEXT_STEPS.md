# Next steps — practical plan

**Last updated:** 2026-05-26

This document is the **high-level “what to do next”** companion to GitHub issues and boards. It is updated when the codebase or priorities change.

---

## Assessment — 2026-05-26

### Summary

MedLocal AI is **reasonably organized for a Streamlit PoC**, not a chaotic prototype. Folder layout by domain (`components/`, `generation/`, `billing/`, `coding/`, etc.) is sound. The main gaps are **repository hygiene**, **dead code from iterative Codex development**, and **documentation** (now being addressed).

### Organization scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Folder structure | 8/10 | Sensible domain split |
| Separation of concerns | 6/10 | Good modules; `app.py` still orchestrates too much |
| Dead code | 4/10 | Unused imports and orphan modules |
| Repo cleanliness | 3/10 → improving | DB, PDFs, venv were in tree; `.gitignore` added |
| In-repo documentation | 5/10 → improving | Strong root README; `docs/` added |
| Testability | 5/10 | Scripts only, no `tests/` package |

### What is working well

- Clear entry point: `streamlit run app.py`
- UI separated into `components/`
- Report pipeline: extract → schema → render → guard → PDF/DB
- Local-first stack: Whisper, Ollama, SQLite
- i18n (Deutsch / English) for UI strings
- Validation scripts under `scripts/`

### What needs attention (priority order)

#### P0 — Done in this session

- [x] `.gitignore` for venv, `data/medlocal.db`, `exports/reports/*.pdf`, `_freeze/`, `__pycache__`
- [x] `docs/` structure and master [ROADMAP.md](ROADMAP.md)
- [x] Git repository initialized; first commit scoped to docs + gitignore

#### P1 — Repo hygiene ✅ (2026-05-26)

- [x] Connect GitHub remote and push `main`
- [x] Verify ignored files are not staged (`data/medlocal.db`, `exports/reports/*.pdf`)
- [x] Remove `_freeze/` from project tree
- [x] Add `.env.example`, pin `requirements.txt`, `data/README.md`, `exports/reports/.gitkeep`

#### P2 — Code cleanup ✅ (2026-05-26)

- [x] Remove unused imports in `app.py` (never called: `build_generation_context`, `build_insurance_ready_fallback_report`, `build_system_prompt`, `build_user_prompt`, `clean_final_report_text`)
- [x] Remove `_report_is_bad()` (defined, never called)
- [x] Retire or reconnect: `generation/context_builder.py`, `generation/fallback_report.py`, `templates/prompts.py` (superseded by inline JSON prompt in `app.py`)
- [x] Remove unused `utils/report_cleaning.py` after consolidating with `validation/final_report_guard.py`
- [x] Trim `utils/medical_codes.py` to `SPECIALTY_ICONS` only (legacy `suggest_codes` unused; moved to `components/input_panel.py`)

#### P3 — Structure (optional refactor)

- [ ] Extract generation workflow from `app.py`
- [ ] Externalize CSS from `theme/theme.py`
- [ ] Provider lists → `data/providers.json`
- [ ] Pin dependency versions in `requirements.txt`

#### P4 — Quality

- [ ] `tests/` with pytest
- [ ] `AGENTS.md` for Cursor/Codex
- [ ] CI running validation scripts

### Dead code reference (P2 completed)

| Symbol / file | Status |
|---------------|--------|
| `app.py` unused imports listed above | Removed |
| `_report_is_bad()` | Removed |
| `context_builder.py` | Removed |
| `fallback_report.py` | Removed |
| `templates/prompts.py` | Removed (inline JSON extraction prompt kept in `app.py`) |
| `report_cleaning.py` | Removed (`final_report_guard` is canonical sanitizer) |
| `medical_codes.py` | Removed; `SPECIALTY_ICONS` moved to `components/input_panel.py` |

### Duplicate logic

Report sanitization is now consolidated in `validation/final_report_guard.py`.

---

## Immediate next actions

1. **Next PR:** Phase 3 structure improvements (see [ROADMAP.md](ROADMAP.md))
2. Consider adding `__init__.py` to `validation/` and `state/` for package consistency
3. **Ongoing:** Log completed work in [PROGRESS.md](PROGRESS.md); log failed experiments in [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md)

---

## Links

- Master phases: [ROADMAP.md](ROADMAP.md)
- App explanation: [APP_OVERVIEW.md](APP_OVERVIEW.md)
- Dev process: [WORKFLOW.md](WORKFLOW.md)
