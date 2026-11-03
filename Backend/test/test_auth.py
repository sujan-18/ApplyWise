from sqlalchemy import select

from app.models import User


def test_register_user(client, db_session):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["full_name"] == "Test User"
    assert response_data["email"] == "testuser@example.com"
    assert "password" not in response_data
    assert "hashed_password" not in response_data

    statement = select(User).where(
        User.email == "testuser@example.com"
    )

    user = db_session.scalar(statement)

    assert user is not None
    assert user.hashed_password != "TestPassword123"

def test_login_user(client):
    # First, register a user
    client.post(
        "/auth/register",
        json={
            "full_name": "Login Test User",
            "email": "loginuser@example.com",
            "password": "TestPassword123",
        },
    )

    # Then, log in with the same credentials
    response = client.post(
        "/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    assert len(response_data["access_token"]) > 0


def test_current_user_profile_requires_login_and_exposes_only_safe_fields(client):
    registration = client.post(
        "/auth/register",
        json={
            "full_name": "Profile User",
            "email": "profileuser@example.com",
            "password": "TestPassword123",
        },
    )
    assert registration.status_code == 201

    unauthenticated = client.get("/auth/me")
    assert unauthenticated.status_code in (401, 403)

    login = client.post(
        "/auth/login",
        json={"email": "profileuser@example.com", "password": "TestPassword123"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    profile = client.get("/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["full_name"] == "Profile User"
    assert profile.json()["email"] == "profileuser@example.com"
    assert "password" not in profile.json()
    assert "hashed_password" not in profile.json()

    updated = client.patch(
        "/auth/me",
        headers=headers,
        json={"full_name": "Jamie Profile", "email": "jamie.profile@example.com"},
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Jamie Profile"
    assert updated.json()["email"] == "jamie.profile@example.com"
    assert "hashed_password" not in updated.json()
