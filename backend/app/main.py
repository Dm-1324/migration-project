from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import batches, evidence, exceptions, migrations, resources, waves
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
    version="1.0.0-phase1",
    description="Read-only M365 tenant-to-tenant migration control plane (Phase 1: data foundation).",
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


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "env": settings.app_env}
