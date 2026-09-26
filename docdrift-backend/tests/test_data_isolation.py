import os
import shutil
import json
import requests
from pathlib import Path

API_BASE = "http://127.0.0.1:8000"
RAW_DOCS_DIR = Path(__file__).parent.parent / "data" / "raw_docs"

def setup_raw_docs(filename, content):
    if RAW_DOCS_DIR.exists():
        shutil.rmtree(RAW_DOCS_DIR)
    
    # We need a v1.0 folder inside to match the version ingestion logic 
    # as docdrift-backend expects versions. Let's see if the path is required.
    # Usually it's data/raw_docs/v1.0/doc.md
    target_dir = RAW_DOCS_DIR / "v1.0"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = target_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def run_isolation_test():
    print("=" * 75)
    print("      DOCDRIFT DATA ISOLATION VERIFICATION (ORG A vs ORG B)")
    print("=" * 75)

    # 1. Create Org A and Org B
    print("\n[1/6] Creating Organizations...")
    org_a_res = requests.post(f"{API_BASE}/auth/organization", json={"name": "Org A"})
    org_b_res = requests.post(f"{API_BASE}/auth/organization", json={"name": "Org B"})
    
    org_a_id = org_a_res.json()["id"]
    org_b_id = org_b_res.json()["id"]
    print(f"-> Org A: {org_a_id}, Org B: {org_b_id}")

    # 2. Register Admin A, Admin B, Employee A
    print("\n[2/6] Registering Users...")
    requests.post(f"{API_BASE}/auth/register", json={
        "email": "admin@orga.com", "password": "Password1!", "role": "admin", "org_id": org_a_id
    })
    requests.post(f"{API_BASE}/auth/register", json={
        "email": "employee@orga.com", "password": "Password1!", "role": "employee", "org_id": org_a_id
    })
    requests.post(f"{API_BASE}/auth/register", json={
        "email": "admin@orgb.com", "password": "Password1!", "role": "admin", "org_id": org_b_id
    })

    # 3. Log in to get tokens
    print("\n[3/6] Acquiring Tokens...")
    token_admin_a = requests.post(f"{API_BASE}/auth/login", json={"email": "admin@orga.com", "password": "Password1!"}).json()["access_token"]
    token_emp_a = requests.post(f"{API_BASE}/auth/login", json={"email": "employee@orga.com", "password": "Password1!"}).json()["access_token"]
    token_admin_b = requests.post(f"{API_BASE}/auth/login", json={"email": "admin@orgb.com", "password": "Password1!"}).json()["access_token"]

    # 4. Ingest as Admin A
    print("\n[4/6] Ingesting documents for Org A...")
    setup_raw_docs("orga_doc.md", "# Org A Secret\nThe launch code for Org A is ALPHA-777.")
    res = requests.post(f"{API_BASE}/ingest", headers={"Authorization": f"Bearer {token_admin_a}"})
    print(f"-> Org A Ingest Result: {res.json()}")

    # 5. Ingest as Admin B
    print("\n[5/6] Ingesting documents for Org B...")
    setup_raw_docs("orgb_doc.md", "# Org B Secret\nThe launch code for Org B is BRAVO-999.")
    res = requests.post(f"{API_BASE}/ingest", headers={"Authorization": f"Bearer {token_admin_b}"})
    print(f"-> Org B Ingest Result: {res.json()}")

    # 6. Verify Isolation
    print("\n[6/6] Verifying isolation as Employee A...")
    
    # 6a. GET /documents
    docs_res = requests.get(f"{API_BASE}/documents", headers={"Authorization": f"Bearer {token_emp_a}"})
    docs = docs_res.json()
    print(f"-> Employee A sees documents: {docs}")
    assert len(docs) == 1, "Employee A should only see 1 document"
    assert docs[0]["source_doc"] == "orga_doc.md", "Employee A should only see Org A's doc"

    # 6b. POST /ask (Querying Org A content)
    ask_a = requests.post(f"{API_BASE}/ask", json={"question": "What is the launch code?", "version": "v1.0"}, headers={"Authorization": f"Bearer {token_emp_a}"})
    print(f"\n-> Q: What is the launch code?")
    print(f"-> A (from Org A context): {ask_a.json()['answer']}")
    assert "ALPHA-777" in ask_a.json()['answer'], "Should have retrieved Org A's launch code"

    # 6c. POST /ask (Trying to query Org B content)
    ask_b = requests.post(f"{API_BASE}/ask", json={"question": "What is the launch code for Org B?", "version": "v1.0"}, headers={"Authorization": f"Bearer {token_emp_a}"})
    print(f"\n-> Q: What is the launch code for Org B?")
    print(f"-> A (from Org B attempt): {ask_b.json()['answer']}")
    assert "BRAVO-999" not in ask_b.json()['answer'], "SECURITY BREACH: Employee A retrieved Org B's launch code!"
    
    print("\n" + "=" * 75)
    print("VERIFICATION COMPLETED: Complete Data Isolation Proven!")
    print("=" * 75)

if __name__ == "__main__":
    run_isolation_test()
