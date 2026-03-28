from dataclasses import replace

from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_health_endpoint_returns_profile():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["profile"] in {"development", "production"}


def test_ready_endpoint_requires_dependency_when_configured(monkeypatch):
    original_settings = main.settings
    monkeypatch.setattr(main, "settings", replace(main.settings, readiness_require_groq=True))
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "dependency_unavailable"

    monkeypatch.setattr(main, "settings", original_settings)


def test_upload_rejects_non_pdf_file():
    response = client.post(
        "/upload",
        files={"file": ("notes.txt", b"plain text", "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_file_type"


def test_upload_returns_demo_when_groq_missing(monkeypatch):
    monkeypatch.setattr(main, "validate_pdf", lambda file_bytes, filename: None)
    monkeypatch.setattr(main, "extract_text_from_pdf", lambda file_bytes: "sample legal text")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    response = client.post(
        "/upload",
        files={"file": ("case.pdf", b"%PDF-1.4 sample", "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["_mode"] == "demo"
    assert "_demo_note" in payload
