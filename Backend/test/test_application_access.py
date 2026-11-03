def test_user_cannot_access_another_users_application(client):
    # Register User A
    client.post(
        "/auth/register",
        json={
            "full_name": "User A",
            "email": "usera@example.com",
            "password": "TestPassword123",
        },
    )

    # Log in as User A
    login_response = client.post(
        "/auth/login",
        json={
            "email": "usera@example.com",
            "password": "TestPassword123",
        },
    )

    token_a = login_response.json()["access_token"]

    headers_a = {
        "Authorization": f"Bearer {token_a}"
    }

    # User A creates an application
    create_response = client.post(
        "/applications/",
        headers=headers_a,
        json={
            "company_name": "F1Soft",
            "job_title": "Python Intern",
            "status": "Applied",
            "notes": "Application created by User A",
        },
    )

    assert create_response.status_code == 201

    application_id = create_response.json()["id"]

    # Register User B
    client.post(
        "/auth/register",
        json={
            "full_name": "User B",
            "email": "userb@example.com",
            "password": "TestPassword123",
        },
    )

    # Log in as User B
    login_response_b = client.post(
        "/auth/login",
        json={
            "email": "userb@example.com",
            "password": "TestPassword123",
        },
    )

    token_b = login_response_b.json()["access_token"]

    headers_b = {
        "Authorization": f"Bearer {token_b}"
    }

    # User B tries to access User A's application
    response = client.get(
        f"/applications/{application_id}",
        headers=headers_b,
    )

    assert response.status_code == 404

    # User B tries to update User A's application
    patch_response = client.patch(
        f"/applications/{application_id}",
        headers=headers_b,
        json={
            "status": "Accepted",
            "notes": "Modified by User B",
        },
    )

    assert patch_response.status_code == 404

    # User B tries to delete User A's application
    delete_response = client.delete(
        f"/applications/{application_id}",
        headers=headers_b,
    )

    assert delete_response.status_code == 404

def test_unauthenticated_user_cannot_access_applications(client):
    # Try to create an application without logging in
    create_response = client.post(
        "/applications/",
        json={
            "company_name": "F1Soft",
            "job_title": "Python Intern",
            "status": "Applied",
        },
    )

    assert create_response.status_code == 401

    # Try to get all applications without logging in
    get_response = client.get("/applications/")

    assert get_response.status_code == 401