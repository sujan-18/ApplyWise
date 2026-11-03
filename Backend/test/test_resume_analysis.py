from io import BytesIO

from docx import Document


DOCX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def make_resume_docx() -> bytes:
    document = Document()
    document.add_paragraph("Demo Candidate")
    document.add_paragraph("Python developer with SQL experience")
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def test_analyze_resume_upload(client, monkeypatch):
    registration = client.post(
        "/auth/register",
        json={
            "full_name": "Resume Test User",
            "email": "resume-test@example.com",
            "password": "TestPassword123",
        },
    )
    assert registration.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "email": "resume-test@example.com",
            "password": "TestPassword123",
        },
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    monkeypatch.setattr(
        "app.routers.ai.analyze_resume",
        lambda text: {"candidate_name": "Demo Candidate"},
    )
    response = client.post(
        "/ai/analyze-resume",
        headers=headers,
        files={
            "file": (
                "resume.docx",
                make_resume_docx(),
                DOCX_CONTENT_TYPE,
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["analysis"] == {"candidate_name": "Demo Candidate"}
    assert response.json()["filename"] == "resume.docx"
    assert response.json()["user_id"] == registration.json()["id"]
    assert client.get("/ai/test", headers=headers).status_code == 404
