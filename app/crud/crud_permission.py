from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.models.models import Permission, Role, User


def get_roles_summary(db: Session, search: str, all: bool, sortColumn: str, sortOrder: str):
    query = (
        select(
            Role.uuid,
            Role.role_title,
            Role.role_description,
            Role.is_custom,
            func.count(User.id).label("count"),
            func.count(User.deleted_at).label("uncounted"),
        )
        .outerjoin(User, User.user_role_id == Role.id)
        .where(Role.deleted_at.is_(None))
        .group_by(Role.uuid, Role.role_title, Role.role_description, Role.is_custom)
        .order_by(text(f"{sortColumn} {sortOrder}"))
    )

    all_filters = []

    if search is not None:
        all_filters.append(Role.role_title.ilike(f"%{search}%"))
        query = query.filter(*all_filters)

    if (all is not None) and (all is False):
        query = query.where(Role.is_system == False)  # noqa: E712

    result = db.execute(query)  # await db.execute(query)

    return result.all()


def get_role_by_uuid(db: Session, uuid: UUID) -> Role | None:
    query = select(Role).where(Role.uuid == uuid).options(selectinload("*"))

    result = db.execute(query)

    return result.scalar_one_or_none()


def get_permission_by_uuid(db: Session, uuid: UUID) -> Permission | None:
    query = select(Permission).where(Permission.uuid == uuid)

    result = db.execute(query)

    return result.scalar_one_or_none()


def get_role_by_name(db: Session, name: str) -> Role | None:
    query = select(Role).where(func.lower(Role.role_title) == name.lower())

    result = db.execute(query)

    return result.scalar_one_or_none()


def get_permissions(db: Session) -> Sequence[Permission]:
    query = select(Permission).order_by(Permission.group.asc(), Permission.id.asc())
    result = db.execute(query)
    return result.scalars().all()


def create_role_with_permissions(db: Session, data: dict) -> Role:
    new_role = Role(**data)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return new_role


def update_role(db: Session, db_role: Role, update_data: dict) -> Role:
    for key, value in update_data.items():
        setattr(db_role, key, value)

    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    return db_role
