from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import Select, func, select, text
from sqlalchemy.orm import Session

from app.models.models import User


def get_users(sort_column: str, sort_order: str, search: str | None = None) -> Select[tuple[User]]:
    query = (
        select(User)
        .where(User.deleted_at.is_(None))
        .where(User.is_visible.is_(True))
        .order_by(text(f"{sort_column} {sort_order}"))
    )

    all_filters = []
    if search is not None:
        all_filters.append(func.concat(User.first_name, " ", User.last_name).ilike(f"%{search}%"))

        query = query.filter(*all_filters)

    return query
    # result = db.execute(query)  # await db.execute(query)
    #
    # return result.scalars().all()


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


def get_user_count(db: Session, user_id: int | None = None) -> int:
    query = (
        select(func.count(User.id))
        .where(User.deleted_at.is_(None))
        .where(User.is_verified.is_(True))
        .where(User.is_visible.is_(True))
    )

    if user_id:
        query = query.where(User.id.isnot(user_id))

    result = db.execute(query)  # await db.execute(query)
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
