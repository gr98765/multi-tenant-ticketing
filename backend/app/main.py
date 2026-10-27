import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import Base, engine
from .routers import auth, dashboard, incidents, releases, services


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No migrations yet: create any missing tables and indexes on startup.
    # create_all skips indexes on tables that already exist, so add those
    # one by one (checkfirst makes this safe to run on every start).
    Base.metadata.create_all(bind=engine)
    for table in Base.metadata.sorted_tables:
        for index in table.indexes:
            index.create(bind=engine, checkfirst=True)
    enable_row_level_security()
    yield


def enable_row_level_security():
    """Lock every table against database-level API access.

    Hosts like Supabase auto-publish tables in the public schema through a
    REST API that anyone with the project's public key can call. With row
    level security on and no policies, that API sees no rows at all. This
    backend connects as the table owner, which bypasses RLS, so the app keeps
    working and all access still goes through FastAPI's auth checks.
    """
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            conn.execute(text(f'ALTER TABLE "{table.name}" ENABLE ROW LEVEL SECURITY'))


app = FastAPI(title="Relay.io — Incident & Release Management", lifespan=lifespan)

# Comma-separated list of allowed frontend origins, e.g.
# CORS_ORIGINS="https://relay-io.vercel.app,http://localhost:5173"
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(services.router)
app.include_router(releases.router)
app.include_router(incidents.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}