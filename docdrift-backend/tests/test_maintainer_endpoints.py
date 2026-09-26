import subprocess
import requests
import uuid

API_BASE = "http://127.0.0.1:8000"

def run_test():
    print("=" * 75)
    print("      DOCDRIFT MAINTAINER ENDPOINTS VERIFICATION")
    print("=" * 75)

    maintainer_email = f"maintainer_{uuid.uuid4().hex[:6]}@docdrift.internal"
    admin_email = f"admin_{uuid.uuid4().hex[:6]}@testorg.com"
    employee_email = f"employee_{uuid.uuid4().hex[:6]}@testorg.com"

    # 1. Seed maintainer (or fallback to existing)
    print("[1] Seeding initial maintainer...")
    try:
        subprocess.run([
            "python", "seed_maintainer.py", 
            "--email", maintainer_email, 
            "--password", "Password1!"
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        if b"already exists" in e.output or b"already exists" in e.stderr:
            print("Maintainer already exists. Falling back to default maintainer.")
            maintainer_email = "maintainer@docdrift.internal"
        else:
            raise e

    # 2. Log in as maintainer
    token_maintainer = requests.post(f"{API_BASE}/auth/login", json={"email": maintainer_email, "password": "Password1!"}).json()["access_token"]
    headers_maintainer = {"Authorization": f"Bearer {token_maintainer}"}

    # 3. Create Organization
    org_res = requests.post(f"{API_BASE}/auth/organization", json={"name": f"Test Org {uuid.uuid4().hex[:6]}"}, headers=headers_maintainer)
    org_id = org_res.json()["id"]
    print(f"-> Created Organization: {org_id}")

    # 4. Register Admin and Employee
    requests.post(f"{API_BASE}/auth/register", json={
        "email": admin_email,
        "password": "Password1!",
        "role": "admin",
        "org_id": org_id
    }, headers=headers_maintainer)

    # Log in as admin
    token_admin = requests.post(f"{API_BASE}/auth/login", json={"email": admin_email, "password": "Password1!"}).json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    requests.post(f"{API_BASE}/auth/register", json={
        "email": employee_email,
        "password": "Password1!",
        "role": "employee"
    }, headers=headers_admin)


    print("\n[Testing with MAINTAINER Token]")
    orgs_res = requests.get(f"{API_BASE}/auth/organizations", headers={"Authorization": f"Bearer {token_maintainer}"})
    print(f"GET /auth/organizations (maintainer) -> {orgs_res.status_code}")
    print(orgs_res.json())
    assert orgs_res.status_code == 200, "Maintainer should get 200 OK"

    users_res = requests.get(f"{API_BASE}/auth/organizations/{org_id}/users", headers={"Authorization": f"Bearer {token_maintainer}"})
    print(f"GET /auth/organizations/{org_id}/users (maintainer) -> {users_res.status_code}")
    print(users_res.json())
    assert users_res.status_code == 200, "Maintainer should get 200 OK"
    
    print("\n[Testing with ADMIN Token (Should be 403 Forbidden)]")
    admin_orgs_res = requests.get(f"{API_BASE}/auth/organizations", headers={"Authorization": f"Bearer {token_admin}"})
    print(f"GET /auth/organizations (admin) -> {admin_orgs_res.status_code}")
    print(admin_orgs_res.json())
    assert admin_orgs_res.status_code == 403, f"Admin should get 403, got {admin_orgs_res.status_code}"

    admin_users_res = requests.get(f"{API_BASE}/auth/organizations/{org_id}/users", headers={"Authorization": f"Bearer {token_admin}"})
    print(f"GET /auth/organizations/{org_id}/users (admin) -> {admin_users_res.status_code}")
    print(admin_users_res.json())
    assert admin_users_res.status_code == 403, f"Admin should get 403, got {admin_users_res.status_code}"

    print("\n" + "=" * 75)
    print("VERIFICATION COMPLETED: Endpoints work for maintainer and reject admin!")
    print("=" * 75)

if __name__ == "__main__":
    run_test()
