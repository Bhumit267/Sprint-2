import os
import subprocess
import requests
import uuid
from pathlib import Path

API_BASE = "http://127.0.0.1:8000"

def run_test():
    print("=" * 75)
    print("      PART 2 VERIFICATION (UPLOAD & DOWNLOAD)")
    print("=" * 75)

    maintainer_email = f"maintainer_{uuid.uuid4().hex[:6]}@docdrift.internal"
    admin_email = f"admin_{uuid.uuid4().hex[:6]}@testorg.com"

    # 1. Seed maintainer
    try:
        subprocess.run([
            "python", "seed_maintainer.py", 
            "--email", maintainer_email, 
            "--password", "Password1!"
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        if b"already exists" in e.output or b"already exists" in e.stderr:
            maintainer_email = "maintainer@docdrift.internal"
        else:
            raise e

    # Log in as maintainer
    token_maintainer = requests.post(f"{API_BASE}/auth/login", json={"email": maintainer_email, "password": "Password1!"}).json()["access_token"]
    headers_maintainer = {"Authorization": f"Bearer {token_maintainer}"}

    # Create Organization
    org_res = requests.post(f"{API_BASE}/auth/organization", json={"name": f"Test Org {uuid.uuid4().hex[:6]}"}, headers=headers_maintainer)
    org_id = org_res.json()["id"]

    # Register Admin
    requests.post(f"{API_BASE}/auth/register", json={
        "email": admin_email,
        "password": "Password1!",
        "role": "admin",
        "org_id": org_id
    }, headers=headers_maintainer)

    # Log in as admin
    token_admin = requests.post(f"{API_BASE}/auth/login", json={"email": admin_email, "password": "Password1!"}).json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    print(f"Logged in as Admin (Org ID: {org_id})")

    # Upload file
    print("\n[1] Uploading test document...")
    test_file_path = Path("test_upload.md")
    test_file_path.write_text("# Test Document\nThis is a test upload.")

    with open(test_file_path, "rb") as f:
        res = requests.post(
            f"{API_BASE}/ingest",
            headers=headers_admin,
            data={"version": "v1.0", "doc_type": "api_reference"},
            files={"file": ("test_upload.md", f, "text/markdown")}
        )
    print(f"POST /ingest -> {res.status_code}")
    print(res.json())
    assert res.status_code == 200, "Upload failed"

    # Get documents
    print("\n[2] Fetching Document Library...")
    docs_res = requests.get(f"{API_BASE}/documents", headers=headers_admin)
    print(f"GET /documents -> {docs_res.status_code}")
    docs = docs_res.json()
    print(docs)
    assert len(docs) > 0, "No documents found"
    
    doc_id = [d["id"] for d in docs if d["source_doc"] == "test_upload.md"][0]
    print(f"Found Postgres record for test_upload.md: ID={doc_id}")

    # Get Download Link
    print(f"\n[3] Fetching Download URL for doc {doc_id}...")
    download_res = requests.get(f"{API_BASE}/documents/{doc_id}/download", headers=headers_admin)
    print(f"GET /documents/{{id}}/download -> {download_res.status_code}")
    download_url = download_res.json()["download_url"]
    print(f"Download URL: {download_url}")
    
    # Try downloading
    print("\n[4] Downloading from signed URL...")
    file_content = requests.get(download_url).text
    print("Content:")
    print(file_content)
    assert "Test Document" in file_content, "Downloaded content didn't match"

    print("\n" + "=" * 75)
    print("PART 2 VERIFICATION COMPLETED: File uploaded, recorded in DB, and downloaded!")
    print("=" * 75)

    test_file_path.unlink()

if __name__ == "__main__":
    run_test()
