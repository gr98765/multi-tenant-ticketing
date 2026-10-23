import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, dashboard, incidents, releases, services


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No migrations yet: create any missing tables on startup (idempotent).
    Base.metadata.create_all(bind=engine)
    yield


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
