from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401
from .database import Base, engine
from .routers import auth, dashboard, incidents, releases, services

Base.metadata.create_all(bind=engine)  # TEMPORARY - creates tables on startup

app = FastAPI(title="Multi-Tenant Ticketing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
