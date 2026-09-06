def test_signup_creates_user_and_returns_token(client):
    response = client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "testpass123",
        "organization_name": "TestOrg",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_signup_duplicate_email_fails(client):
    client.post("/auth/signup", json={
        "email": "dupe@example.com",
        "password": "testpass123",
        "organization_name": "TestOrg",
    })
    response = client.post("/auth/signup", json={
        "email": "dupe@example.com",
        "password": "anotherpass",
        "organization_name": "TestOrg2",
    })
    assert response.status_code == 400


def test_login_with_wrong_password_fails(client):
    client.post("/auth/signup", json={
        "email": "user@example.com",
        "password": "correctpass",
        "organization_name": "TestOrg",
    })
    response = client.post("/auth/login", data={
        "username": "user@example.com",
        "password": "wrongpass",
    })
    assert response.status_code == 401
