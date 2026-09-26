"""Authentication API router providing registration, login, and org creation."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, hash_password, verify_password
from app.auth.dependencies import get_current_user, require_role
from app.models.db import Organization, User, UserRole, get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str
    org_id: Optional[str] = None


class RegisterResponse(BaseModel):
    id: str
    email: str
    role: str
    org_id: Optional[str]
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    organization_name: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class CreateOrgRequest(BaseModel):
    name: str


class OrgResponse(BaseModel):
    id: str
    name: str
    created_at: datetime


class OrgWithCountsResponse(BaseModel):
    id: str
    name: str
    admin_count: int
    employee_count: int


class UserInOrgResponse(BaseModel):
    email: str
    role: str


@router.post(
    "/organization",
    response_model=OrgResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization tenant",
)
def create_organization(
    payload: CreateOrgRequest,
    current_user: Dict[str, Any] = Depends(require_role("maintainer")),
    db: Session = Depends(get_db),
) -> OrgResponse:
    """Creates a new organization record."""
    name = payload.name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name cannot be empty",
        )

    existing = db.query(Organization).filter(Organization.name == name).first()
    if existing:
        return OrgResponse(id=existing.id, name=existing.name, created_at=existing.created_at)

    org = Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return OrgResponse(id=org.id, name=org.name, created_at=org.created_at)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account with role and org assignment",
)
def register_user(
    payload: RegisterRequest,
    current_user: Dict[str, Any] = Depends(require_role("maintainer", "admin")),
    db: Session = Depends(get_db),
) -> RegisterResponse:
    """Registers a new user account."""
    email = payload.email.strip().lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email cannot be empty",
        )

    # Validate role enum
    role_str = payload.role.strip().lower()
    try:
        user_role = UserRole(role_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{role_str}'. Allowed roles: {[r.value for r in UserRole]}",
        )

    # Enforce role-to-org rules based on caller's role
    caller_role = current_user.get("role")
    
    if caller_role == "admin":
        if user_role == UserRole.MAINTAINER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot create maintainer accounts.",
            )
        # Override org_id securely to the admin's own organization
        org_id = current_user.get("org_id")
        if payload.org_id and payload.org_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admins can only create users for their own organization.",
            )
    else:
        # Caller is maintainer
        org_id = payload.org_id.strip() if payload.org_id else None
        
        if user_role == UserRole.MAINTAINER:
            if org_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maintainers must not belong to any specific organization (org_id must be null).",
                )
        else:
            # Maintainer creating Admin or Employee requires a valid org_id
            if not org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role '{user_role.value}' requires a valid org_id.",
                )
            # Verify organization exists
            org = db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Organization with id '{org_id}' not found.",
                )

    # Check for duplicate email
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{email}' already exists.",
        )

    # Hash password and create user
    hashed = hash_password(payload.password)
    user = User(
        email=email,
        hashed_password=hashed,
        role=user_role,
        org_id=org_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        org_id=user.org_id,
        message="User registered successfully",
    )


@router.post(
    "/signup",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Public self-serve signup (Creates Org + Admin)",
)
def signup_organization(
    payload: SignupRequest,
    db: Session = Depends(get_db),
) -> RegisterResponse:
    """Creates a new organization and the founding admin account."""
    org_name = payload.organization_name.strip()
    email = payload.email.strip().lower()
    
    if not org_name or not email or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name, email, and password are required.",
        )
        
    # Check if org exists
    if db.query(Organization).filter(Organization.name == org_name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization '{org_name}' already exists.",
        )
        
    # Check if user exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{email}' already exists.",
        )
        
    # Create Org
    org = Organization(name=org_name)
    db.add(org)
    db.flush() # flush to get org.id
    
    # Create Admin User
    hashed = hash_password(payload.password)
    user = User(
        email=email,
        hashed_password=hashed,
        role=UserRole.ADMIN,
        org_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return RegisterResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        org_id=user.org_id,
        message="Organization and Admin created successfully",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue signed JWT token",
)
def login_user(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Verifies credentials and issues a signed JWT containing user_id, role, and org_id."""
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
    token = create_access_token(
        user_id=user.id,
        role=role_val,
        org_id=user.org_id,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "role": role_val,
            "org_id": user.org_id,
        },
    )


@router.get(
    "/me",
    summary="Get currently authenticated user identity and claims",
)
def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Returns the authenticated user's profile and verified claims."""
    return current_user


@router.get(
    "/organizations",
    response_model=List[OrgWithCountsResponse],
    summary="List all organizations with user counts (Maintainer only)",
)
def list_organizations(
    current_user: Dict[str, Any] = Depends(require_role("maintainer")),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Returns all organizations and their admin/employee counts."""
    orgs = db.query(Organization).all()
    results = []
    for org in orgs:
        admin_count = db.query(User).filter(User.org_id == org.id, User.role == UserRole.ADMIN).count()
        employee_count = db.query(User).filter(User.org_id == org.id, User.role == UserRole.EMPLOYEE).count()
        results.append({
            "id": org.id,
            "name": org.name,
            "admin_count": admin_count,
            "employee_count": employee_count,
        })
    return results


@router.get(
    "/organizations/{org_id}/users",
    response_model=List[UserInOrgResponse],
    summary="List users in an organization (Maintainer or Org Member)",
)
def list_organization_users(
    org_id: str,
    current_user: Dict[str, Any] = Depends(require_role("maintainer", "admin", "employee")),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Returns the list of users in a specific organization."""
    caller_role = current_user.get("role")
    if caller_role in ["admin", "employee"]:
        if current_user.get("org_id") != org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view members of this organization.",
            )

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    users = db.query(User).filter(User.org_id == org_id).all()
    return [
        {
            "email": u.email,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
        }
        for u in users
    ]

