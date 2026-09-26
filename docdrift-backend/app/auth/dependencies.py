"""FastAPI authentication dependencies for token verification and role enforcement."""

from typing import Any, Callable, Dict, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.models.db import User, get_db

# Bearer token extractor from Authorization header
security_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Validates JWT bearer token from Authorization header and returns current user info.

    Returns:
        dict: Containing user_id, role, org_id, and email.

    Raises:
        HTTPException: 401 Unauthorized if missing, expired, or invalid.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header or Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims: user_id missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists in database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    org_name = user.organization.name if user.organization else None

    return {
        "id": user.id,
        "user_id": user.id,
        "email": user.email,
        "role": role_str,
        "org_id": user.org_id,
        "org_name": org_name,
    }


def require_role(*roles: str) -> Callable[..., Dict[str, Any]]:
    """Dependency factory wrapping get_current_user and enforcing permitted roles.

    Raises:
        HTTPException: 403 Forbidden if user's role is not within the permitted list.
    """
    allowed_roles = set(roles)

    def role_dependency(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{user_role}' is not authorized. Allowed: {list(allowed_roles)}",
            )
        return current_user

    return role_dependency
