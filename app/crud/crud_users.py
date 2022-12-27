from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.models import User


def get_users(db: Session, search: str, sortColumn: str, sortOrder: str) -> User:
    all_filters = []

    if search is not None:
        all_filters.append(func.concat(User.first_name, " ", User.last_name).ilike(f"%{search}%"))

    return db.execute(select(User).filter(*all_filters).order_by(text(f"{sortColumn} {sortOrder}"))).scalars().all()


def get_user_by_uuid(db: Session, uuid: UUID) -> User:
    return db.execute(select(User).where(User.uuid == uuid)).scalar_one_or_none()


def get_user_by_id(db: Session, id: int) -> User:
    return db.execute(select(User).where(User.id == id)).scalar_one_or_none()


def get_user_by_email(db: Session, email: EmailStr) -> User:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def get_user_count(db: Session) -> int:
    return db.execute(select(func.count(User.id))).scalar_one_or_none()


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
