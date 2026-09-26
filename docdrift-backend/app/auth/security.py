"""Security, password hashing, and JWT token operations for DocDrift."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import bcrypt
import jwt

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)


def hash_password(password: str) -> str:
    """Hashes a plain password using bcrypt (max 72 bytes)."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against an existing bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    user_id: str,
    role: str,
    org_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates a signed JWT access token containing user_id, role, and org_id claims."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "user_id": str(user_id),
        "role": str(role),
        "org_id": str(org_id) if org_id else None,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a signed JWT token.

    Raises:
        ValueError: If the token has expired or signature is invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Authentication token has expired")
    except jwt.PyJWTError as e:
        raise ValueError(f"Invalid authentication token: {str(e)}")
