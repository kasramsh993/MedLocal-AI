# Ideas and future work

**Last updated:** 2026-05-26

High-level backlog and experiments. **Actionable near-term tasks** live in [NEXT_STEPS.md](NEXT_STEPS.md). **Execution order** lives in [ROADMAP.md](ROADMAP.md). Use GitHub issues for assignable tickets.

---

## Product ideas

- Replace mock ICD-10-GM / EBM / GOÄ with licensed or official datasets
- Specialty-specific Arztbrief templates (e.g. Kardiologie vs. Allgemeinmedizin)
- Version history for drafts (compare transcript → v1 → approved)
- Multi-user / practice login and audit trail for approvals
- Export formats beyond PDF (HL7 FHIR DocumentReference, plain DOCX)
- Offline model management UI (pull/switch Ollama models from the app)

## Technical ideas

- Extract generation workflow from `app.py` into `workflows/`
- Pin dependencies and add `pyproject.toml` / `uv` lockfile
- pytest suite + GitHub Actions CI
- `AGENTS.md` for consistent Cursor + Codex instructions
- External CSS file for theme; dark mode
- Structured logging and request IDs for support debugging
- Environment-based config (`config.toml` / `.env`) for model name, DB path, export dir

## UX / i18n

- More complete English UI parity
- Accessibility review (contrast, keyboard, screen readers)
- Clearer empty states when Ollama or Whisper is unavailable

## Compliance and deployment (long term)

- DSGVO documentation: processing register, DPIA checklist
- Encryption at rest for `medlocal.db`
- Deployment guide: Docker, reverse proxy, backup of DB + exports
- Role separation: assistant vs. approver physician

---

## How to add an idea

1. Add a short bullet here with date if helpful.
2. If it becomes near-term work, copy a one-liner into [NEXT_STEPS.md](NEXT_STEPS.md).
3. Create a GitHub issue when ready to implement.
