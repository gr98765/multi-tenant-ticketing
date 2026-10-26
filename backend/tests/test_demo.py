"""The one-click demo company."""
import random
from datetime import datetime

from scripts import seed

from app.demo import DEMO_EMAIL, DEMO_ORG
from conftest import create_service, signup


def _load_demo(rng_seed=1):
    seed.delete_demo_org()
    rows = seed._offset_ids(seed.generate(random.Random(rng_seed), 1, 90,
                                          datetime.utcnow(), demo=True,
                                          with_updates=True))
    seed.load(dict(zip(seed.COLUMNS, rows)))


def _demo_headers(client):
    resp = client.post("/auth/demo")
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_demo_login_unavailable_until_seeded(client):
    assert client.post("/auth/demo").status_code == 404


def test_demo_login_opens_populated_demo_company_as_member(client, db_session):
    _load_demo()
    h = _demo_headers(client)

    me = client.get("/auth/me", headers=h).json()
    assert me == {"email": DEMO_EMAIL,
                  "role": "MEMBER", "organization_name": DEMO_ORG}

    report = client.get("/dashboard/reliability", headers=h).json()
    assert len(report["services"]) == 6
    assert report["deploys"] > 0 and report["failed_deploys"] > 0
    assert client.get("/dashboard/", headers=h).json()["recent_releases"]
    assert client.get("/incidents/assigned-to-me", headers=h).json()


def test_demo_visitor_cannot_destroy_demo_data(client, db_session):
    _load_demo()
    h = _demo_headers(client)
    service = client.get("/services/", headers=h).json()[0]["id"]
    release = client.get("/releases/", headers=h).json()[0]["id"]

    assert client.delete(f"/services/{service}", headers=h).status_code == 403
    assert client.delete(f"/releases/{release}", headers=h).status_code == 403
    assert client.post("/auth/invite", json={"email": "x@y.z", "password": "pw12345"},
                       headers=h).status_code == 403


def test_demo_reset_replaces_demo_only_and_keeps_real_signups(client, db_session):
    real = signup(client, "real@customer.com", "RealCo")
    create_service(client, real, "real-service")
    _load_demo(rng_seed=1)
    h = _demo_headers(client)
    junk = client.get("/services/", headers=h).json()[0]["id"]
    client.post("/incidents/", json={"title": "junk test test 123", "severity": "SEV4",
                                     "service_id": junk}, headers=h)

    _load_demo(rng_seed=2)  # the scheduled reset

    h = _demo_headers(client)
    titles = [i["title"] for i in client.get("/incidents/", headers=h).json()]
    assert "junk test test 123" not in titles
    assert [s["name"] for s in client.get("/services/", headers=real).json()] == [
        "real-service"]
    # the real customer still can't see demo data, and vice versa
    assert client.get("/incidents/", headers=real).json() == []
