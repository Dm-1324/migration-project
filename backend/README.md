# M365 Migration PM Agent — Backend

Phases 1–3 of the V1 M365 tenant-to-tenant migration control plane.

## Phase 3

- Deterministic mock Entra, Exchange Online and OneDrive/SharePoint adapters.
- Typed `assess_entra`, `assess_exchange`, and `assess_onedrive` capabilities.
- Evidence-first persistence and blocking/warning exception creation.
- Failure simulation with explicit `UNAVAILABLE` / `NOT_READY` behavior.
- `start_batch_assessment` as the Phase 3 stand-in for Copilot Studio `WF_AssessBatch`.
- Compact Copilot context endpoints.
- Human-code resolver endpoints for migration and batch codes.
- Completed assessment runs are immutable; retries create a new run.

## Run

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

## Test

```powershell
python -m pytest tests/ -v
```

Phase 3 was verified from a clean extraction with the full suite passing before publication.

## Phase 4 boundary

Copilot Studio should call the typed tool and resolver APIs. It must not calculate readiness itself or write lifecycle state directly. `WF_AssessBatch` will replace the Phase 3 one-shot orchestration with deterministic workflow orchestration in Copilot Studio.
