from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Tag


def get_tags(db: Session) -> Tag:
    return db.execute(select(Tag).where(Tag.deleted_at.is_(None))).scalars().all()


def get_tag_by_uuid(db: Session, uuid: UUID) -> Tag:
    query = select(Tag).where(Tag.uuid == uuid)

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
