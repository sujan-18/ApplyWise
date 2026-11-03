def test_create_application_with_invalid_data(client):
    # Register a user
    client.post(
        "/auth/register",
        json={
            "full_name": "Validation User",
            "email": "validation@example.com",
            "password": "TestPassword123",
        },
    )

    # Log in
    login_response = client.post(
        "/auth/login",
        json={
            "email": "validation@example.com",
            "password": "TestPassword123",
        },
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Send invalid application data
    response = client.post(
        "/applications/",
        headers=headers,
        json={
            "company_name": "F",
            "job_title": "",
            "status": "Something Invalid",
        },
    )

    assert response.status_code == 422