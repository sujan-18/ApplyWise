
def register_and_login(client):
    user_data = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPassword123",
    }

    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def create_application(client, headers, company_name, application_status="Applied"):
    return client.post(
        "/applications/",
        headers=headers,
        json={
            "company_name": company_name,
            "job_title": "Python Developer Intern",
            "status": application_status,
            "notes": "Test application",
        },
    )


def test_default_pagination_returns_maximum_ten_applications(client):
    headers = register_and_login(client)

    for number in range(12):
        response = create_application(
            client,
            headers,
            f"Company {number}",
        )
        assert response.status_code == 201

    response = client.get("/applications/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 10


def test_pagination_skip_and_limit(client):
    headers = register_and_login(client)

    for number in range(5):
        create_application(client, headers, f"Company {number}")

    first_page = client.get(
        "/applications/?skip=0&limit=2",
        headers=headers,
    )

    second_page = client.get(
        "/applications/?skip=2&limit=2",
        headers=headers,
    )

    assert first_page.status_code == 200
    assert second_page.status_code == 200

    first_ids = {item["id"] for item in first_page.json()}
    second_ids = {item["id"] for item in second_page.json()}

    assert len(first_ids) == 2
    assert len(second_ids) == 2
    assert first_ids.isdisjoint(second_ids)


def test_filter_applications_by_status(client):
    headers = register_and_login(client)

    create_application(client, headers, "Company A", "Applied")
    create_application(client, headers, "Company B", "Rejected")
    create_application(client, headers, "Company C", "Applied")

    response = client.get(
        "/applications/?status=Applied",
        headers=headers,
    )

    assert response.status_code == 200

    applications = response.json()

    assert len(applications) == 2
    assert all(item["status"] == "Applied" for item in applications)


def test_filter_and_pagination_together(client):
    headers = register_and_login(client)

    for number in range(5):
        create_application(client, headers, f"Company {number}", "Applied")

    response = client.get(
        "/applications/?status=Applied&skip=1&limit=2",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 2

    assert all(
        item["status"] == "Applied"
        for item in response.json()
    )


def test_invalid_pagination_parameters(client):
    headers = register_and_login(client)

    invalid_urls = [
        "/applications/?skip=-1",
        "/applications/?limit=0",
        "/applications/?limit=101",
        "/applications/?status=Unknown",
    ]

    for url in invalid_urls:
        response = client.get(url, headers=headers)
        assert response.status_code == 422
