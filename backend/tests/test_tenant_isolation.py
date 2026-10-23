"""Every org-scoped resource must be invisible to other organizations.

Org B gets a valid token and then tries to read, change or delete each of
Org A's resources by ID. All attempts must fail with 404 (we don't even
confirm the resource exists), and Org A's data must be unchanged.
"""
import pytest

from conftest import create_incident, create_release, create_service, signup


@pytest.fixture()
def two_orgs(client):
    org_a = signup(client, "alice@a.com", "OrgA")
    org_b = signup(client, "bob@b.com", "OrgB")
    service = create_service(client, org_a, "a-payments")
    release = create_release(client, org_a, service, "v1.0.0")
    incident = create_incident(client, org_a, service, release_id=release)
    alice_id = client.get("/auth/members", headers=org_a).json()[0]["id"]
    return {"a": org_a, "b": org_b, "service": service, "release": release,
            "incident": incident, "alice_id": alice_id}


CROSS_TENANT_ATTEMPTS = [
    ("get", "/services/{service}", None),
    ("delete", "/services/{service}", None),
    ("delete", "/releases/{release}", None),
    ("get", "/incidents/{incident}", None),
    ("patch", "/incidents/{incident}/status", {"status": "RESOLVED"}),
    ("get", "/incidents/{incident}/updates", None),
    ("post", "/incidents/{incident}/updates", {"message": "hijacked"}),
    ("patch", "/incidents/{incident}/assign?user_id={alice_id}", None),
    ("post", "/releases/", {"service_id": "{service}", "version": "evil"}),
    ("post", "/incidents/", {"title": "x", "severity": "SEV1",
                             "service_id": "{service}"}),
]


def _fill(value, ids):
    if isinstance(value, str):
        filled = value.format(**ids)
        return int(filled) if filled.isdigit() else filled
    if isinstance(value, dict):
        return {k: _fill(v, ids) for k, v in value.items()}
    return value


@pytest.mark.parametrize("method,path,body", CROSS_TENANT_ATTEMPTS,
                         ids=[f"{m.upper()} {p}" for m, p, _ in CROSS_TENANT_ATTEMPTS])
def test_other_org_cannot_touch_resource(client, two_orgs, method, path, body):
    kwargs = {"headers": two_orgs["b"]}
    if body is not None:
        kwargs["json"] = _fill(body, two_orgs)
    resp = getattr(client, method)(_fill(path, two_orgs), **kwargs)
    assert resp.status_code == 404, resp.text

    # Org A's data is untouched
    a = two_orgs["a"]
    incident = client.get(f"/incidents/{two_orgs['incident']}", headers=a).json()
    assert incident["status"] == "OPEN"
    assert incident["release_id"] == two_orgs["release"]
    updates = client.get(f"/incidents/{two_orgs['incident']}/updates", headers=a)
    assert updates.json() == []
    assert len(client.get("/releases/", headers=a).json()) == 1


@pytest.mark.parametrize("path", ["/services/", "/releases/", "/incidents/",
                                  "/incidents/assigned-to-me"])
def test_other_org_lists_are_empty(client, two_orgs, path):
    assert client.get(path, headers=two_orgs["b"]).json() == []


def test_other_org_members_are_hidden(client, two_orgs):
    members = client.get("/auth/members", headers=two_orgs["b"]).json()
    emails = [m["email"] for m in members]
    assert emails == ["bob@b.com"]


def test_cannot_assign_incident_to_user_in_another_org(client, two_orgs):
    b = two_orgs["b"]
    service = create_service(client, b, "b-api")
    incident = create_incident(client, b, service)
    resp = client.patch(f"/incidents/{incident}/assign?user_id={two_orgs['alice_id']}",
                        headers=b)
    assert resp.status_code == 404


def test_cannot_link_incident_to_another_orgs_release(client, two_orgs):
    b = two_orgs["b"]
    service = create_service(client, b, "b-api")
    resp = client.post("/incidents/", json={
        "title": "x", "severity": "SEV2", "service_id": service,
        "release_id": two_orgs["release"],
    }, headers=b)
    assert resp.status_code == 404


def test_dashboards_only_count_own_data(client, two_orgs):
    b = two_orgs["b"]
    dash = client.get("/dashboard/", headers=b).json()
    assert dash["open_incidents"] == 0
    assert dash["service_stats"] == []
    rel = client.get("/dashboard/reliability", headers=b).json()
    assert rel["deploys"] == 0 and rel["services"] == []
