import sys
import argparse
from sqlalchemy.orm import Session
from app.models.db import SessionLocal, User, UserRole
from app.auth.security import hash_password

def seed_maintainer(email: str, password: str):
    db: Session = SessionLocal()
    try:
        existing_maintainer = db.query(User).filter(User.role == UserRole.MAINTAINER).first()
        if existing_maintainer:
            print(f"[-] A maintainer already exists ({existing_maintainer.email}). Bootstrapping aborted.")
            sys.exit(1)

        hashed = hash_password(password)
        maintainer = User(
            email=email.strip().lower(),
            hashed_password=hashed,
            role=UserRole.MAINTAINER,
            org_id=None
        )
        db.add(maintainer)
        db.commit()
        print(f"[+] Successfully seeded the initial maintainer account: {maintainer.email}")
    except Exception as e:
        db.rollback()
        print(f"[-] Failed to seed maintainer: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap the initial maintainer account.")
    parser.add_argument("--email", required=True, help="Email for the maintainer account")
    parser.add_argument("--password", required=True, help="Password for the maintainer account")
    args = parser.parse_args()

    seed_maintainer(args.email, args.password)
