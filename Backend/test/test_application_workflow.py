def test_user_can_track_application_through_interview_and_delete(client):
    registration = client.post(
        "/auth/register",
        json={
            "full_name": "Workflow User",
            "email": "workflow@example.com",
            "password": "WorkflowPass123",
        },
    )
    assert registration.status_code == 201
    assert "hashed_password" not in registration.json()

    login = client.post(
        "/auth/login",
        json={"email": "workflow@example.com", "password": "WorkflowPass123"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = client.post(
        "/applications/",
        headers=headers,
        json={
            "company_name": "Northstar Labs",
            "job_title": "Software Intern",
            "status": "Applied",
            "applied_date": "2026-11-03",
            "notes": "Follow up next week",
        },
    )
    assert created.status_code == 201
    application = created.json()
    application_id = application["id"]
    assert application["company_name"] == "Northstar Labs"
    assert application["job_title"] == "Software Intern"
    assert application["status"] == "Applied"
    assert application["applied_date"] == "2026-11-03"
    assert application["notes"] == "Follow up next week"

    listed = client.get("/applications/?limit=100", headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [application_id]

    updated = client.patch(
        f"/applications/{application_id}",
        headers=headers,
        json={"status": "Interview", "notes": "Interview next Tuesday"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "Interview"
    assert updated.json()["notes"] == "Interview next Tuesday"

    filtered = client.get("/applications/?status=Interview", headers=headers)
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1
    assert filtered.json()[0]["id"] == application_id

    detail = client.get(f"/applications/{application_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["company_name"] == "Northstar Labs"

    deleted = client.delete(f"/applications/{application_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get("/applications/?limit=100", headers=headers).json() == []
    assert client.get(f"/applications/{application_id}", headers=headers).status_code == 404


def test_frontend_and_cors_are_available(client):
    frontend = client.get("/app/")
    assert frontend.status_code == 200
    assert "ApplyWise" in frontend.text

    login_page = client.get("/app/login.html")
    assert login_page.status_code == 200
    assert 'id="login-form"' in login_page.text

    preflight = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "http://localhost:3001"
