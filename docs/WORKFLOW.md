# Development workflow — Cursor, Codex, GitHub

**Last updated:** 2026-05-26

How we develop MedLocal AI across tools without losing context.

---

## Roles of each tool

| Tool | Best for |
|------|----------|
| **Cursor** | Day-to-day editing, refactors, running app locally, reading codebase |
| **Codex (ChatGPT)** | Larger exploratory changes, alternative implementations, documentation drafts |
| **GitHub** | Source of truth, issues/boards, PR review, CI (when added) |
| **`docs/`** | Why, architecture, progress, failed attempts, master roadmap |

---

## Branching

- Default branch: **`main`**
- Feature work: `feature/<short-description>` or issue number `feature/12-icd-cleanup`
- Keep PRs small: docs-only, dead-code-only, or one feature per PR

---

## Before you commit

1. `git status` — ensure **no** `data/medlocal.db`, `exports/reports/*.pdf`, `.venv/`, or `_freeze/` are staged
2. Run relevant checks:
   ```bash
   python scripts/validate_demo_reports.py
   python scripts/validate_time_savings.py
   ```
3. Manual smoke test if UI changed: `streamlit run app.py` (see root README checklist)

---

## After a merged change

1. Add a dated entry to [PROGRESS.md](PROGRESS.md)
2. If an experiment failed, log it in [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md)
3. Update [NEXT_STEPS.md](NEXT_STEPS.md) if priorities changed
4. Mark [ROADMAP.md](ROADMAP.md) phase steps done when a whole phase completes

---

## Connecting GitHub (first time)

From the project root (after initial commit):

```bash
git remote add origin https://github.com/<org-or-user>/<repo>.git
git branch -M main
git push -u origin main
```

Replace the URL with your repository. If the remote already exists on GitHub with content, coordinate `pull --rebase` or force-push only if you intend to overwrite remote history.

---

## What never goes to GitHub

- `data/medlocal.db` (may contain demo/patient-like data)
- `exports/reports/*.pdf`
- `.venv/`
- `_freeze/` backup bundles
- Secrets: `.env`, API keys
- Private notes: anything under `docs/_local/` except `docs/_local/README.md`

Mock JSON under `data/icd10gm/` and `data/billing/` **is** committed.

---

## Suggested prompts for agents

When starting a task in Cursor or Codex, point to:

- `docs/NEXT_STEPS.md` — current priorities
- `docs/ROADMAP.md` — which phase we are in
- `docs/FAILED_ATTEMPTS.md` — do not repeat retired approaches
- `docs/ARCHITECTURE.md` — where code lives

Example: *“Implement ROADMAP Phase 2.1: remove unused imports in app.py per NEXT_STEPS dead code table. Do not change generation behavior.”*

---

## Issues vs. docs

| Use GitHub issues for | Use `docs/` for |
|----------------------|-----------------|
| Assignable tasks, bugs, PR links | Phases, architecture, lessons learned |
| Sprint / board columns | Assessment and roadmap |
| Code review discussion | Plain-language app explanation |
