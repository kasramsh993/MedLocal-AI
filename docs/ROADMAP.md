# Master plan — MedLocal AI organization

**Created:** 2026-05-26  
**Status:** Active — update this file when phases complete or priorities change.

This is the committed step-by-step plan. GitHub issues/boards track individual tasks; this document tracks **phases and order**.

---

## Phase 0 — Repository foundation ✅

| Step | Action | Status |
|------|--------|--------|
| 0.1 | Add `.gitignore` (venv, DB, PDFs, `_freeze`, `docs/_local/*`) | Done |
| 0.2 | Initialize git repository | Done |
| 0.3 | Add `docs/` structure and populate core documents | Done |
| 0.4 | Initial commit: `.gitignore` + `docs/` only | Done |
| 0.5 | Connect GitHub remote and push `main` | Done |

---

## Phase 1 — Repo hygiene (no behavior change) ✅

| Step | Action | Status |
|------|--------|--------|
| 1.1 | Confirm `data/medlocal.db` and `exports/reports/*.pdf` stay untracked | Done |
| 1.2 | Remove or relocate `_freeze/` baseline bundles from active development | Done (folder removed) |
| 1.3 | Add `.env.example` if environment variables are introduced | Done |
| 1.4 | Pin or narrow `requirements.txt` versions for reproducible installs | Done |

---

## Phase 2 — Dead code and clarity ✅

| Step | Action | Status |
|------|--------|--------|
| 2.1 | Remove unused imports in `app.py` (`context_builder`, `fallback_report`, `prompts`, `report_cleaning`, etc.) | Done |
| 2.2 | Delete or wire orphaned modules: `context_builder.py`, `fallback_report.py`, unused `templates/prompts.py` path | Done (files removed) |
| 2.3 | Remove legacy functions in `utils/medical_codes.py` (`suggest_codes`, `split_code_suggestions`) | Done (`SPECIALTY_ICONS` moved into `input_panel.py`) |
| 2.4 | Remove unused `_report_is_bad()` in `app.py` | Done |
| 2.5 | Consolidate report sanitization into one module (`final_report_guard` vs `report_cleaning`) | Done (`final_report_guard` retained) |

---

## Phase 3 — Structure and maintainability

| Step | Action | Status |
|------|--------|--------|
| 3.1 | Add `__init__.py` to `validation/` and `state/` for consistency | Done |
| 3.2 | Move generation orchestration out of `app.py` (e.g. `workflows/generation.py`) |
| 3.3 | Externalize theme CSS from `theme/theme.py` to a static file |
| 3.4 | Move GKV/PKV provider lists to `data/` JSON |
| 3.5 | Add module docstrings on public entry points |

---

## Phase 4 — Quality and collaboration

| Step | Action |
|------|--------|
| 4.1 | Add `tests/` with pytest for validators, ICD search, billing optimizer |
| 4.2 | Add `AGENTS.md` or `.cursor/rules` for Cursor + Codex conventions |
| 4.3 | Add `LICENSE` and `CONTRIBUTING.md` when collaboration is formalized |
| 4.4 | CI: lint + run `scripts/validate_*.py` on push |

---

## Phase 5 — Product (only when legally and technically ready)

| Step | Action |
|------|--------|
| 5.1 | Real ICD-10-GM / EBM / GOÄ data sources (replace mocks) |
| 5.2 | Hardening for production patient data (DSGVO, audit, access control) |
| 5.3 | Deployment guide (Docker, reverse proxy, backups) |

---

## How to use this roadmap

1. After each merged change, update [PROGRESS.md](PROGRESS.md).
2. When an experiment fails, add an entry to [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md).
3. When priorities shift, update [NEXT_STEPS.md](NEXT_STEPS.md) and this file.
4. Link GitHub issue numbers in PROGRESS entries when helpful.
