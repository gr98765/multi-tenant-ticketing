from conftest import create_incident, create_release, create_service, invite, signup


def test_create_and_list_services(client):
    headers = signup(client, "a@example.com", "OrgA")
    create_service(client, headers, "payments-api")
    resp = client.get("/services/", headers=headers)
    assert resp.status_code == 200
    assert [s["name"] for s in resp.json()] == ["payments-api"]


def test_incident_lifecycle_open_investigating_resolved(client):
    headers = signup(client, "user@example.com", "OrgC")
    service_id = create_service(client, headers, "web-app")
    incident_id = create_incident(client, headers, service_id, severity="SEV1")

    incident = client.get(f"/incidents/{incident_id}", headers=headers).json()
    assert incident["status"] == "OPEN"

    # first timeline update moves it to INVESTIGATING
    resp = client.post(f"/incidents/{incident_id}/updates",
                       json={"message": "Looking into it"}, headers=headers)
    assert resp.status_code == 200
    incident = client.get(f"/incidents/{incident_id}", headers=headers).json()
    assert incident["status"] == "INVESTIGATING"

    resp = client.patch(f"/incidents/{incident_id}/status",
                        json={"status": "RESOLVED"}, headers=headers)
    assert resp.json()["status"] == "RESOLVED"
    assert resp.json()["resolved_at"] is not None

    updates = client.get(f"/incidents/{incident_id}/updates", headers=headers).json()
    assert [u["message"] for u in updates] == ["Looking into it"]


def test_reopening_an_incident_clears_resolved_at(client):
    headers = signup(client, "user@example.com", "OrgC")
    service_id = create_service(client, headers)
    incident_id = create_incident(client, headers, service_id)
    client.patch(f"/incidents/{incident_id}/status", json={"status": "RESOLVED"},
                 headers=headers)
    resp = client.patch(f"/incidents/{incident_id}/status",
                        json={"status": "INVESTIGATING"}, headers=headers)
    assert resp.json()["resolved_at"] is None


def test_incident_can_be_linked_to_its_release(client):
    headers = signup(client, "user@example.com", "OrgC")
    service_id = create_service(client, headers)
    release_id = create_release(client, headers, service_id, "v2.0.0")
    incident_id = create_incident(client, headers, service_id, release_id=release_id)
    incident = client.get(f"/incidents/{incident_id}", headers=headers).json()
    assert incident["release_id"] == release_id


def test_release_from_another_service_is_rejected(client):
    headers = signup(client, "user@example.com", "OrgC")
    web = create_service(client, headers, "web-app")
    api = create_service(client, headers, "api")
    api_release = create_release(client, headers, api)
    resp = client.post("/incidents/", json={
        "title": "x", "severity": "SEV3", "service_id": web, "release_id": api_release,
    }, headers=headers)
    assert resp.status_code == 404


def test_deleting_a_release_keeps_its_incidents(client):
    headers = signup(client, "user@example.com", "OrgC")
    service_id = create_service(client, headers)
    release_id = create_release(client, headers, service_id)
    incident_id = create_incident(client, headers, service_id, release_id=release_id)
    assert client.delete(f"/releases/{release_id}", headers=headers).status_code == 204
    incident = client.get(f"/incidents/{incident_id}", headers=headers).json()
    assert incident["release_id"] is None


def test_assign_incident_and_list_assigned_to_me(client):
    owner = signup(client, "owner@example.com", "OrgC")
    member = invite(client, owner, "oncall@example.com")
    service_id = create_service(client, owner)
    incident_id = create_incident(client, owner, service_id)
    member_id = next(m["id"] for m in client.get("/auth/members", headers=owner).json()
                     if m["email"] == "oncall@example.com")

    resp = client.patch(f"/incidents/{incident_id}/assign?user_id={member_id}",
                        headers=owner)
    assert resp.status_code == 200
    mine = client.get("/incidents/assigned-to-me", headers=member).json()
    assert [i["id"] for i in mine] == [incident_id]
