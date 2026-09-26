"""Authentication package for DocDrift multi-tenant access control."""

from app.auth.security import create_access_token, decode_access_token, hash_password, verify_password
from app.auth.dependencies import get_current_user, require_role
from app.auth.router import router as auth_router

__all__ = [
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
    "get_current_user",
    "require_role",
    "auth_router",
]
