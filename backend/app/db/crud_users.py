"""CRUD operations for User model."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from app.models.schemas import User
from app.core.security import get_password_hash


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address."""
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.get(User, user_id)


def create_user(db: Session, email: str, password: str, full_name: Optional[str] = None) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_last_login(db: Session, user: User) -> User:
    """Update user's last login timestamp."""
    # Note: We'd need to add last_login_at column to User model in production
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> bool:
    """Soft delete a user by setting is_active to False."""
    user.is_active = False
    db.commit()
    return True


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    """Get all users with pagination."""
    return db.execute(select(User).offset(skip).limit(limit)).scalars().all()
