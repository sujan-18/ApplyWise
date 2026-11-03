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