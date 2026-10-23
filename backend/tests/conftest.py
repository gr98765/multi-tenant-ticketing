import os

# Tests run against a real PostgreSQL database (the analytics use
# Postgres-only SQL). Point the app at it before anything imports it.
os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://ticketing:ticketing@localhost:5432/ticketing_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402

TABLES = "incident_updates, incidents, releases, services, users, organizations"


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))


@pytest.fixture()
def client(db_session):
    with TestClient(app) as c:
        yield c


# ---- helpers shared by test modules ----

def signup(client, email, org_name, password="testpass123"):
    resp = client.post("/auth/signup", json={
        "email": email, "password": password, "organization_name": org_name,
    })
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def invite(client, owner_headers, email, password="memberpass1"):
    resp = client.post("/auth/invite", json={"email": email, "password": password},
                       headers=owner_headers)
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def create_service(client, headers, name="payments-api"):
    resp = client.post("/services/", json={"name": name}, headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()["id"]


def create_release(client, headers, service_id, version="v1.0.0"):
    body = {"service_id": service_id, "version": version}
    resp = client.post("/releases/", json=body, headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()["id"]


def create_incident(client, headers, service_id, release_id=None, title="Outage",
                    severity="SEV2"):
    resp = client.post("/incidents/", json={
        "title": title, "severity": severity,
        "service_id": service_id, "release_id": release_id,
    }, headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()["id"]
