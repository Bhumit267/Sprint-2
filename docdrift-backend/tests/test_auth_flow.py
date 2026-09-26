"""Test script verifying database models, registration, login, JWT payload decoding, and get_current_user dependency for DocDrift multi-tenancy."""

import json
import requests
import jwt

API_BASE = "http://127.0.0.1:8000"


def run_auth_verification():
    print("=" * 75)
    print("      DOCDRIFT MULTI-TENANCY & AUTHENTICATION VERIFICATION")
    print("=" * 75)

    # 1. Create an Organization
    org_payload = {"name": "Acme Global"}
    print(f"\n[1/4] Creating Organization: {org_payload['name']}...")
    org_res = requests.post(f"{API_BASE}/auth/organization", json=org_payload)
    if org_res.status_code not in (200, 201):
        raise RuntimeError(f"Failed to create organization: {org_res.text}")

    org_data = org_res.json()
    org_id = org_data["id"]
    print(f"-> Organization Created: ID = {org_id}, Name = '{org_data['name']}'")

    # 2. Register Accounts
    # 2a. Maintainer (org_id must be None)
    print("\n[2/4] Registering Accounts...")
    maintainer_payload = {
        "email": "maintainer.verify@docdrift.internal",
        "password": "MaintainerPassword123!",
        "role": "maintainer",
        "org_id": None,
    }
    m_res = requests.post(f"{API_BASE}/auth/register", json=maintainer_payload)
    if m_res.status_code not in (200, 201) and "already exists" not in m_res.text:
        raise RuntimeError(f"Failed to register maintainer: {m_res.text}")
    print(f"-> Maintainer: {maintainer_payload['email']} (role: maintainer, org_id: None)")

    # 2b. Admin (belongs to Acme Global)
    admin_payload = {
        "email": "admin.verify@acme.com",
        "password": "AdminPassword123!",
        "role": "admin",
        "org_id": org_id,
    }
    a_res = requests.post(f"{API_BASE}/auth/register", json=admin_payload)
    if a_res.status_code not in (200, 201) and "already exists" not in a_res.text:
        raise RuntimeError(f"Failed to register admin: {a_res.text}")
    print(f"-> Admin: {admin_payload['email']} (role: admin, org_id: {org_id})")

    # 2c. Employee (belongs to Acme Global)
    employee_payload = {
        "email": "employee.verify@acme.com",
        "password": "EmployeePassword123!",
        "role": "employee",
        "org_id": org_id,
    }
    e_res = requests.post(f"{API_BASE}/auth/register", json=employee_payload)
    if e_res.status_code not in (200, 201) and "already exists" not in e_res.text:
        raise RuntimeError(f"Failed to register employee: {e_res.text}")
    print(f"-> Employee: {employee_payload['email']} (role: employee, org_id: {org_id})")

    # 3. Log in as each user
    print("\n[3/4] Logging in and acquiring JWT tokens...")

    accounts = [
        ("Maintainer", maintainer_payload["email"], maintainer_payload["password"]),
        ("Admin", admin_payload["email"], admin_payload["password"]),
        ("Employee", employee_payload["email"], employee_payload["password"]),
    ]

    tokens = {}
    for role_name, email, password in accounts:
        login_res = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password},
        )
        if login_res.status_code != 200:
            raise RuntimeError(f"Login failed for {role_name} ({email}): {login_res.text}")

        login_data = login_res.json()
        token = login_data["access_token"]
        tokens[role_name] = token
        print(f"-> {role_name} logged in successfully. Token acquired.")

        # Test GET /auth/me with Bearer token
        me_res = requests.get(
            f"{API_BASE}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_res.status_code == 200, f"get_current_user failed: {me_res.text}"

    # 4. Decode JWT payloads
    print("\n[4/4] ALL THREE DECODED JWT PAYLOADS:")
    print("=" * 75)

    decoded_results = {}
    for role_name, token in tokens.items():
        decoded = jwt.decode(token, options={"verify_signature": False})
        decoded_results[role_name] = decoded

        print(f"\n=======================================================")
        print(f"  ROLE: {role_name.upper()}")
        print(f"=======================================================")
        print(json.dumps(decoded, indent=2))

        # Assert correct claims structure
        assert "user_id" in decoded, f"Missing user_id in {role_name} token"
        assert "role" in decoded, f"Missing role in {role_name} token"
        assert "org_id" in decoded, f"Missing org_id in {role_name} token"

        if role_name == "Maintainer":
            assert decoded["role"] == "maintainer"
            assert decoded["org_id"] is None, "Maintainer org_id must be None"
        elif role_name == "Admin":
            assert decoded["role"] == "admin"
            assert decoded["org_id"] == org_id, "Admin org_id mismatch"
        elif role_name == "Employee":
            assert decoded["role"] == "employee"
            assert decoded["org_id"] == org_id, "Employee org_id mismatch"

    print("\n" + "=" * 75)
    print("VERIFICATION COMPLETED: All 3 roles created, logged in, and verified!")
    print("=" * 75)


if __name__ == "__main__":
    run_auth_verification()
