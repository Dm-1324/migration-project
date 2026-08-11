"""
FastAPI application entrypoint.

All routes are mounted under /api/v1 per section 12 of the V1 doc.
This process owns: REST API, auth boundary (added in a later phase), SQL
access, business services -- never M365 credentials directly (section 4.3).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    assessments,
    audit,
    batches,
    evidence,
    exceptions,
    lifecycle,
    migrations,
    readiness,
    resources,
    runs,
    waves,
)
from app.config import get_settings
from app.database import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="M365 Migration PM Agent API",
    version="1.0.0-phase2",
    description="Read-only M365 tenant-to-tenant migration control plane (Phase 2: deterministic readiness engine).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(migrations.router, prefix=API_PREFIX)
app.include_router(waves.router, prefix=API_PREFIX)
app.include_router(batches.router, prefix=API_PREFIX)
app.include_router(resources.router, prefix=API_PREFIX)
app.include_router(evidence.router, prefix=API_PREFIX)
app.include_router(exceptions.router, prefix=API_PREFIX)
app.include_router(assessments.router, prefix=API_PREFIX)
app.include_router(readiness.router, prefix=API_PREFIX)
app.include_router(runs.router, prefix=API_PREFIX)
app.include_router(audit.router, prefix=API_PREFIX)
app.include_router(lifecycle.router, prefix=API_PREFIX)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "env": settings.app_env}
