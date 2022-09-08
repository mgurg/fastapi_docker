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


def get_roles_by_uuid(db: Session, uuid: UUID):
    return db.execute(select(Role).where(Role.uuid == uuid).options(selectinload("*"))).scalar_one_or_none()


def get_permissions(db: Session):
    return db.execute(select(Permission)).scalars().all()
