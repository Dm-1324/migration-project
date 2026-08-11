# M365 Migration PM Agent Platform

V1 backend for the M365 tenant-to-tenant migration control plane.

## Current status

- **Phase 1 — Data foundation**: FastAPI, SQLAlchemy, Alembic, CRUD, evidence and exceptions.
- **Phase 2 — Deterministic readiness**: assessments, domain result contracts, readiness policy, lifecycle gates and audit trail.
- **No M365 production writes** are implemented yet.

The architecture keeps readiness and lifecycle decisions deterministic. Copilot Studio will orchestrate the system in a later phase; it does not override backend policy.

## Backend quick start

### Windows PowerShell

```powershell
git clone https://github.com/Dm-1324/migration-project.git
cd migration-project\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs**.

### Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

Expected: **13 tests passing**.

## Phase 2 API surface

| Method | Endpoint |
|---|---|
| POST | `/api/v1/batches/{batch_id}/assessments` |
| GET | `/api/v1/batches/{batch_id}/assessments` |
| GET | `/api/v1/assessments/{assessment_id}` |
| POST | `/api/v1/assessments/{assessment_id}/domains/result` |
| GET | `/api/v1/batches/{batch_id}/assessments/{domain}` |
| GET | `/api/v1/readiness/{batch_id}` |
| POST | `/api/v1/readiness/{batch_id}/calculate` |
| GET | `/api/v1/runs/{run_id}` |
| GET | `/api/v1/runs/{run_id}/status` |
| GET | `/api/v1/audit` |
| POST | `/api/v1/batches/{batch_id}/lifecycle/transition` |

## Readiness policy

The backend calculates readiness in this order:

1. Missing/stale domain → `NOT_READY`
2. Unavailable/error domain → `NOT_READY`
3. Any blocked domain → `BLOCKED`
4. Any warning domain → `WARNING`
5. Otherwise → `READY`

Only `READY` permits `PREFLIGHT_PASS` or `READY` lifecycle transitions.

## Next phases

1. **Phase 3** — mock Entra / Exchange Online / OneDrive tools and failure simulation.
2. **Phase 4** — Microsoft Copilot Studio PM + specialist agents and workflows.
3. **Phase 5** — Next.js frontend and PM chat/dashboard.
4. **Phase 6** — real M365 read-only integrations.
5. **Phase 7** — hardening, security, observability and production readiness.
