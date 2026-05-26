# Progress log

Dated record of **completed** milestones. For planned work, see [ROADMAP.md](ROADMAP.md) and [NEXT_STEPS.md](NEXT_STEPS.md).

---

## 2026-05-26 — Phase 1 repo hygiene

**What we did**

- Removed `_freeze/` baseline bundle from the project tree (back up elsewhere if needed)
- Added `.env.example` (`APP_DEBUG`)
- Pinned `requirements.txt` to versions tested in local `.venv`
- Added `data/README.md` and `exports/reports/.gitkeep`
- Verified `data/medlocal.db` and `exports/reports/*.pdf` remain gitignored

**Related**

- [ROADMAP.md](ROADMAP.md) Phase 1

---

## 2026-05-26 — Documentation and repository foundation

**What we did**

- Added root `.gitignore` (venv, SQLite DB, exported PDFs, `_freeze/`, local scratch under `docs/_local/`)
- Created `docs/` structure: overview, architecture, roadmap, next steps, progress, ideas, failed attempts, workflow
- Recorded codebase assessment in `docs/NEXT_STEPS.md` (2026-05-26)
- Initialized git repository; first commit contains `.gitignore` and `docs/` only (application code unchanged in that commit scope)

**Notes**

- PoC application code remains as generated; cleanup tracked in Phase 2 of [ROADMAP.md](ROADMAP.md)
- GitHub remote connection and push left to project owner

**Related**

- Assessment: [NEXT_STEPS.md](NEXT_STEPS.md)
- Plan: [ROADMAP.md](ROADMAP.md) Phase 0

---

## Template for future entries

```markdown
## YYYY-MM-DD — Short title

**What we did**
- Bullet points

**Notes**
- Optional context, PR/issue links

**Related**
- #issue or PR URL
```
