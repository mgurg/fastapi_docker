from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.models.models import UserGroup


def get_user_groups(db: Session, search: str, sortColumn: str, sortOrder: str):
    all_filters = []

    if search is not None:
        all_filters.append(UserGroup.name.ilike(f"%{search}%"))

    return (
        db.execute(select(UserGroup).filter(*all_filters).order_by(text(f"{sortColumn} {sortOrder}"))).scalars().all()
    )


def get_user_group_by_uuid(db: Session, uuid: UUID) -> UserGroup:
    # return db.execute(select(UserGroup).where(UserGroup.uuid == uuid).options(selectinload("*"))).scalar_one_or_none()
    return db.execute(select(UserGroup).where(UserGroup.uuid == uuid).options(selectinload("*"))).scalar_one_or_none()


def get_user_group_by_name(db: Session, name: str) -> UserGroup:
    return db.execute(select(UserGroup).where(func.lower(UserGroup.name) == name.lower())).scalar_one_or_none()


def create_group_with_users(db: Session, data: dict) -> UserGroup:
    new_group = UserGroup(**data)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group


# def get_roles(db: Session):
#     return db.execute(
#         select(Role.uuid, Role.role_title, Role.role_description, Role.is_custom, func.count(User.id).label("count"))
#         .outerjoin(User, User.user_role_id == Role.id)
#         .group_by(Role.uuid, Role.role_title, Role.role_description, Role.is_custom)
#         .order_by(Role.is_custom)
#     ).all()


# def get_permission_by_uuid(db: Session, uuid: UUID) -> Permission:
#     return db.execute(select(Permission).where(Permission.uuid == uuid)).scalar_one_or_none()


def update_user_group(db: Session, db_group: UserGroup, update_data: dict) -> UserGroup:
    for key, value in update_data.items():
        setattr(db_group, key, value)

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    return db_group
