# Data directory

| Path | In git? | Purpose |
|------|---------|---------|
| `icd10gm/icd10gm_mock.json` | Yes | Mock ICD-10-GM search corpus |
| `billing/billing_codes_mock.json` | Yes | Mock EBM / GOÄ billing codes |
| `medlocal.db` | **No** (local only) | SQLite store for approved reports — created at runtime |

Do not commit `medlocal.db` or other `*.db` files (see root `.gitignore`).
