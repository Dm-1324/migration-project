# M365 Migration PM Agent Platform

V1 backend for the Microsoft 365 tenant-to-tenant migration control plane.

## Current status

- **Phase 1 — Data foundation**: FastAPI, SQLAlchemy, Alembic, CRUD, evidence and exceptions.
- **Phase 2 — Deterministic readiness**: assessments, domain result contracts, readiness policy, lifecycle gates and audit trail.
- **Phase 3 — Mock M365 tools**: deterministic Entra, Exchange Online and OneDrive/SharePoint adapters, typed tool APIs, failure simulation and Copilot context/resolver APIs.
- **No real M365 production calls or production writes** are implemented yet.

The architecture keeps readiness and lifecycle decisions deterministic. Copilot Studio will orchestrate the system in Phase 4; it does not override backend policy.

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

The shipped Phase 3 suite includes the Phase 1/2 tests plus mock-adapter, failure-simulation, immutable-assessment and Copilot-resolver coverage.

## Phase 3 API surface

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/tools/assess_entra` | Run Entra readiness tool for an assessment |
| POST | `/api/v1/tools/assess_exchange` | Run Exchange Online readiness tool |
| POST | `/api/v1/tools/assess_onedrive` | Run OneDrive/SharePoint readiness tool |
| POST | `/api/v1/tools/start_batch_assessment/{batchId}` | Phase 3 stand-in for `WF_AssessBatch` |
| GET | `/api/v1/tools/get_blockers/{batchId}` | Return open blocking exceptions |
| GET | `/api/v1/copilot/batches/{batchId}/context` | Compact authoritative PM context |
| GET | `/api/v1/copilot/migrations/{migrationId}/context` | Compact migration context |
| GET | `/api/v1/resolve/migrations/{migrationCode}` | Resolve human migration code to UUID |
| GET | `/api/v1/resolve/batches/{batchCode}` | Resolve human batch code to UUID; use `migration_code` if ambiguous |

### Failure simulation

The assessment tool accepts only these simulated error codes:

`M365_TIMEOUT`, `M365_THROTTLED`, `AUTH_FAILED`, `RESOURCE_NOT_FOUND`, `UNKNOWN`.

A simulated M365 failure becomes `UNAVAILABLE` at the domain level and `NOT_READY` overall; it never becomes `READY`.

### Assessment immutability

Once an assessment run is `COMPLETED`, its domain results and verdict are frozen. A retry creates a new assessment run rather than mutating the completed run.

## Architecture boundary

```text
Copilot Studio (Phase 4)
        |
        v
Typed FastAPI tool endpoints
        |
        +--> Entra mock adapter
        +--> Exchange mock adapter
        +--> OneDrive/SharePoint mock adapter
        |
        v
Evidence + Exceptions + Assessment
        |
        v
Deterministic Readiness Engine
        |
        v
Authoritative SQL state
```

Phase 6 replaces the mock adapter internals with real Microsoft Graph / Exchange / SharePoint calls without changing the tool or readiness contracts.

## Next phases

1. **Phase 4** — Microsoft Copilot Studio PM + specialist agents and `WF_AssessBatch`.
2. **Phase 5** — Next.js frontend and PM chat/dashboard.
3. **Phase 6** — real M365 read-only integrations.
4. **Phase 7** — security, observability, evaluation, E2E hardening and production readiness.
