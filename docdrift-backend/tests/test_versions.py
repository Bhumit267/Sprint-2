import requests
from pathlib import Path
import shutil

API_BASE = "http://127.0.0.1:8000"
RAW_DOCS_DIR = Path(__file__).parent.parent / "data" / "raw_docs"

def setup_raw_docs(version, filename, content):
    if RAW_DOCS_DIR.exists():
        shutil.rmtree(RAW_DOCS_DIR)
    
    target_dir = RAW_DOCS_DIR / version
    target_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = target_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def test_versions():
    # Login as Admin A
    token_admin_a = requests.post(f"{API_BASE}/auth/login", json={"email": "admin@orga.com", "password": "Password1!"}).json()["access_token"]
    
    # Login as Admin B
    token_admin_b = requests.post(f"{API_BASE}/auth/login", json={"email": "admin@orgb.com", "password": "Password1!"}).json()["access_token"]

    # Ingest v3.0 for Admin A
    setup_raw_docs("v3.0", "orga_doc3.md", "# Org A Secret 3.0")
    requests.post(f"{API_BASE}/ingest", headers={"Authorization": f"Bearer {token_admin_a}"})

    # Ingest v4.0 for Admin B
    setup_raw_docs("v4.0", "orgb_doc4.md", "# Org B Secret 4.0")
    requests.post(f"{API_BASE}/ingest", headers={"Authorization": f"Bearer {token_admin_b}"})

    versions_a = requests.get(f"{API_BASE}/versions", headers={"Authorization": f"Bearer {token_admin_a}"}).json()
    versions_b = requests.get(f"{API_BASE}/versions", headers={"Authorization": f"Bearer {token_admin_b}"}).json()

    print(f"Admin A versions: {versions_a}")
    print(f"Admin B versions: {versions_b}")

if __name__ == "__main__":
    test_versions()
