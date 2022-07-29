from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import User


def get_users(db: Session, skip: int = 0, limit: int = 100) -> User:
    return db.execute(select(User).offset(skip).limit(limit)).scalars().all()


def get_user_by_uuid(db: Session, uuid: UUID) -> User:
    return db.execute(select(User).where(User.uuid == uuid)).scalar_one_or_none()


def get_user_by_email(db: Session, email: EmailStr) -> User:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def create_user(db: Session, data: dict) -> User:
    new_user = User(**data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def update_user(db: Session, db_user: User, update_data: dict) -> User:
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
