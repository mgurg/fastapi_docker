from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.models import Permission, Role, User


def get_roles(db: Session):
    return db.execute(
        select(Role.uuid, Role.role_title, Role.role_description, Role.is_custom, func.count(User.id).label("count"))
        .outerjoin(User, User.user_role_id == Role.id)
        .group_by(Role.uuid, Role.role_title, Role.role_description, Role.is_custom)
        .order_by(Role.is_custom)
    ).all()


def get_role_by_uuid(db: Session, uuid: UUID) -> Role:
    return db.execute(select(Role).where(Role.uuid == uuid).options(selectinload("*"))).scalar_one_or_none()


def get_permission_by_uuid(db: Session, uuid: UUID) -> Permission:
    return db.execute(select(Permission).where(Permission.uuid == uuid)).scalar_one_or_none()


def get_role_by_name(db: Session, name: str) -> Role:
    return db.execute(select(Role).where(Role.role_title == name)).scalar_one_or_none()


def get_permissions(db: Session):
    return db.execute(select(Permission).order_by(Permission.group)).scalars().all()


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
