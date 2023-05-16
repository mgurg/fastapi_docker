from collections.abc import Sequence
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.models import User


def get_users(db: Session, sort_column: str, sort_order: str, search: str | None = None) -> Sequence[User]:
    query = select(User).order_by(text(f"{sort_column} {sort_order}"))

    all_filters = []
    if search is not None:
        all_filters.append(func.concat(User.first_name, " ", User.last_name).ilike(f"%{search}%"))

        query = query.filter(*all_filters)

    result = db.execute(query)  # await db.execute(query)

    return result.scalars().all()


def get_user_by_uuid(db: Session, uuid: UUID) -> User:
    query = select(User).where(User.uuid == uuid)

    result = db.execute(query)

    return result.scalar_one_or_none()


def get_users_by_role_id(db: Session, id: int):
    query = (
        select(User.uuid, User.first_name, User.last_name)
        .where(User.user_role_id == id)
        .where(User.deleted_at.is_(None))
    )

    result = db.execute(query)

    return result.all()


def get_user_by_id(db: Session, id: int) -> User:
    query = select(User).where(User.id == id)

    result = db.execute(query)

    return result.scalar_one_or_none()


def get_user_by_email(db: Session, email: EmailStr) -> User:
    query = select(User).where(User.email == email).where(User.deleted_at.is_(None))

    result = db.execute(query)

    return result.scalar_one_or_none()


def get_user_count(db: Session) -> int:
    query = select(func.count(User.id)).where(User.deleted_at.is_(None)).where(User.is_verified.is_(True))

    result = db.execute(query)

    return result.scalar_one_or_none()


def create_user(db: Session, data: dict) -> User:
    new_user = User(**data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def bulk_insert(db: Session, data: dict) -> bool:
    db.bulk_insert_mappings(User, data)
    db.commit()

    return True


def update_user(db: Session, db_user: User, update_data: dict) -> User:
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
