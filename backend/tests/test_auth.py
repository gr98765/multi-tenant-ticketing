from conftest import create_service, invite, signup


def test_signup_creates_user_and_returns_token(client):
    resp = client.post("/auth/signup", json={
        "email": "test@example.com", "password": "testpass123",
        "organization_name": "TestOrg",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_signup_duplicate_email_fails(client):
    signup(client, "dupe@example.com", "TestOrg")
    resp = client.post("/auth/signup", json={
        "email": "dupe@example.com", "password": "anotherpass",
        "organization_name": "TestOrg2",
    })
    assert resp.status_code == 400


def test_signup_duplicate_org_name_fails(client):
    signup(client, "a@example.com", "SameOrg")
    resp = client.post("/auth/signup", json={
        "email": "b@example.com", "password": "testpass123",
        "organization_name": "SameOrg",
    })
    assert resp.status_code == 400


def test_login_with_wrong_password_fails(client):
    signup(client, "user@example.com", "TestOrg", password="correctpass")
    resp = client.post("/auth/login", data={
        "username": "user@example.com", "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_login_succeeds_and_me_returns_profile(client):
    signup(client, "user@example.com", "TestOrg", password="correctpass")
    resp = client.post("/auth/login", data={
        "username": "user@example.com", "password": "correctpass",
    })
    assert resp.status_code == 200
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    me = client.get("/auth/me", headers=headers).json()
    assert me == {"email": "user@example.com", "role": "OWNER",
                  "organization_name": "TestOrg"}


def test_requests_without_token_are_rejected(client):
    assert client.get("/services/").status_code == 401
    bad = {"Authorization": "Bearer not-a-real-token"}
    assert client.get("/services/", headers=bad).status_code == 401


def test_members_list_never_exposes_password_hashes(client):
    owner = signup(client, "owner@example.com", "TestOrg")
    invite(client, owner, "member@example.com")
    members = client.get("/auth/members", headers=owner).json()
    assert {m["email"] for m in members} == {"owner@example.com", "member@example.com"}
    for m in members:
        assert set(m) == {"id", "email", "role"}


def test_member_cannot_invite_or_manage_services(client):
    owner = signup(client, "owner@example.com", "TestOrg")
    member = invite(client, owner, "member@example.com")
    service_id = create_service(client, owner)

    resp = client.post("/auth/invite", json={"email": "x@example.com",
                       "password": "pw123456"}, headers=member)
    assert resp.status_code == 403
    assert client.post("/services/", json={"name": "new"},
                       headers=member).status_code == 403
    assert client.delete(f"/services/{service_id}", headers=member).status_code == 403
    # but members can still read
    assert client.get("/services/", headers=member).status_code == 200
