"""Automated tests for FastAPI endpoints: /ask, /documents, /ingest, and CORS."""

from pathlib import Path
import sys
from fastapi.testclient import TestClient

# Ensure backend root is in Python sys.path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root health check."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("[PASS] GET / status ok")


def test_ingest_endpoint():
    """Verify POST /ingest pipeline trigger."""
    response = client.post("/ingest")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["documents_processed"] >= 7
    assert data["indexed_chunks"] >= 7
    print(f"[PASS] POST /ingest -> Processed {data['documents_processed']} docs, {data['indexed_chunks']} chunks")


def test_documents_endpoint():
    """Verify GET /documents returns deduplicated list of indexed files."""
    response = client.get("/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 7
    for doc in docs:
        assert "source_doc" in doc
        assert "doc_type" in doc
        assert "version" in doc
    print(f"[PASS] GET /documents -> Returned {len(docs)} indexed documents")


def test_ask_endpoint_success():
    """Verify POST /ask with version-matching query."""
    payload = {
        "question": "How do I get a user's address in version 2.1?",
        "version": "v2.1",
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["is_refusal"] is False
    assert len(data["citations"]) > 0
    assert data["citations"][0]["version"] == "v2.1"
    print(f"[PASS] POST /ask (success query) -> Answer generated with {len(data['citations'])} citations")


def test_ask_endpoint_refusal():
    """Verify POST /ask handles non-existent features with is_refusal=True."""
    payload = {
        "question": "How do I use batchFetchAddresses in v2.1?",
        "version": "v2.1",
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["is_refusal"] is True
    assert len(data["citations"]) == 0
    print("[PASS] POST /ask (refusal query) -> Correctly flagged is_refusal=True with 0 citations")


def test_cors_headers():
    """Verify CORS headers allow http://localhost:3000."""
    response = client.options(
        "/ask",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    print("[PASS] CORS middleware -> Access-Control-Allow-Origin: http://localhost:3000")


if __name__ == "__main__":
    print("\n=== Testing FastAPI Endpoints ===")
    test_root_endpoint()
    test_ingest_endpoint()
    test_documents_endpoint()
    test_ask_endpoint_success()
    test_ask_endpoint_refusal()
    test_cors_headers()
    print("\n[ALL API TESTS PASSED SUCCESSFULLY!]")
