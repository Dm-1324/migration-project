# M365 Migration PM Agent Platform

V1 implementation repository for the M365 tenant-to-tenant migration control plane.

## Current status

**Phase 1 — Data Foundation**

The repository currently contains the runnable FastAPI backend with SQLAlchemy models, Alembic migrations, CRUD APIs, evidence/exception persistence, and tests.

## Repository layout

```text
backend/
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   └── services/
├── alembic/
├── tests/
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md
```

## Quick start

### Windows PowerShell

```powershell
git clone https://github.com/Dm-1324/migration-project.git
cd migration-project\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs**.

### Run tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest tests/ -v
```

For macOS/Linux, use `python3 -m venv .venv` and `source .venv/bin/activate` instead.

## V1 roadmap

1. Data foundation
2. Deterministic readiness engine
3. Mock M365 tools
4. Microsoft Copilot Studio agents/workflows
5. Next.js frontend
6. Real M365 read-only integrations
7. Hardening and observability
