from uuid import UUID

from sqlalchemy import not_, select, text
from sqlalchemy.orm import Session

from app.models.models import Tag


def get_tags(db: Session, sort_column: str, sort_order: str, is_hidden: bool | None = None) -> Tag:
    query = select(Tag).where(Tag.deleted_at.is_(None))

    if is_hidden is True:
        query = query.where(not_(Tag.is_hidden.is_(True)))

    query = query.order_by(text(f"{sort_column} {sort_order}"))

    result = db.execute(query)

    return result.scalars().all()


def get_tag_by_uuid(db: Session, uuid: UUID) -> Tag:
    query = select(Tag).where(Tag.uuid == uuid)

    result = db.execute(query)

    return result.scalar_one_or_none()

def get_tag_by_name(db: Session, name: str) -> Tag:
    query = select(Tag).where(Tag.name == name).where(Tag.deleted_at.is_(None))

    result = db.execute(query)

    return result.scalar_one_or_none()

def get_tags_id_by_uuid(db: Session, uuid: list[UUID]) -> Tag:
    query = select(Tag.id).filter(Tag.uuid.in_(uuid))

    result = db.execute(query)

    return result.scalars().all()


def create_tag(db: Session, data: dict) -> Tag:
    new_tag = Tag(**data)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag


def update_tag(db: Session, db_tag: Tag, update_data: dict) -> Tag:
    for key, value in update_data.items():
        setattr(db_tag, key, value)

    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)

    return db_tag
