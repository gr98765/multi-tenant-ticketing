def _signup_and_get_token(client, email, org_name):
    response = client.post("/auth/signup", json={
        "email": email,
        "password": "testpass123",
        "organization_name": org_name,
    })
    return response.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_services(client):
    token = _signup_and_get_token(client, "a@example.com", "OrgA")
    headers = _auth_headers(token)

    response = client.post(
        "/services/", json={"name": "payments-api"}, headers=headers)
    assert response.status_code == 200

    response = client.get("/services/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "payments-api"


def test_organizations_cannot_see_each_others_services(client):
    token_a = _signup_and_get_token(client, "a@example.com", "OrgA")
    token_b = _signup_and_get_token(client, "b@example.com", "OrgB")

    client.post(
        "/services/", json={"name": "org-a-service"}, headers=_auth_headers(token_a))

    # Org B should see zero services, not Org A's service
    response = client.get("/services/", headers=_auth_headers(token_b))
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_create_incident_and_update_status(client):
    token = _signup_and_get_token(client, "user@example.com", "OrgC")
    headers = _auth_headers(token)

    service_resp = client.post(
        "/services/", json={"name": "web-app"}, headers=headers)
    service_id = service_resp.json()["id"]

    incident_resp = client.post("/incidents/", json={
        "title": "Site is down",
        "severity": "SEV1",
        "service_id": service_id,
    }, headers=headers)
    assert incident_resp.status_code == 200
    incident_id = incident_resp.json()["id"]
    assert incident_resp.json()["status"] == "OPEN"

    update_resp = client.patch(
        f"/incidents/{incident_id}/status", json={"status": "RESOLVED"}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "RESOLVED"
    assert update_resp.json()["resolved_at"] is not None
