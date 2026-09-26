"""SQLAlchemy database models and engine setup for DocDrift multi-tenancy.

Defines Organization and User models with role-based access control.
"""

from datetime import datetime
import enum
import uuid
from typing import Generator
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    create_engine,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
    validates,
    Session,
)

from app.config import DATABASE_URL

Base = declarative_base()


class UserRole(str, enum.Enum):
    """Enumeration of user roles within DocDrift."""
    MAINTAINER = "maintainer"
    ADMIN = "admin"
    EMPLOYEE = "employee"


class Organization(Base):
    """Organization entity representing a tenant domain."""
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Organization(id='{self.id}', name='{self.name}')>"


class User(Base):
    """User account entity with role and tenant affiliation."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    organization = relationship("Organization", back_populates="users")

    @validates("org_id", "role")
    def validate_org_role(self, key: str, value: any):
        """Enforces that org_id is nullable only for maintainer, and required for admin/employee."""
        target_role = value if key == "role" else self.role
        target_org = value if key == "org_id" else self.org_id

        if target_role == UserRole.MAINTAINER:
            if target_org is not None:
                raise ValueError("Maintainers must not belong to any specific organization (org_id must be None).")
        elif target_role in (UserRole.ADMIN, UserRole.EMPLOYEE):
            if key == "org_id" and target_org is None:
                raise ValueError(f"{target_role.value.capitalize()}s must belong to an organization (org_id required).")

        return value

    def __repr__(self) -> str:
        return f"<User(id='{self.id}', email='{self.email}', role='{self.role.value}', org_id='{self.org_id}')>"


class Document(Base):
    """Record of an uploaded file in Supabase Storage."""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(512), nullable=False)
    doc_type = Column(String(50), nullable=False)
    version = Column(String(50), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    organization = relationship("Organization")

    def __repr__(self) -> str:
        return f"<Document(id='{self.id}', filename='{self.filename}', version='{self.version}')>"


# Connection engine & session factory
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Postgres doesn't need check_same_thread
    engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initializes the database schema."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for managing database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
