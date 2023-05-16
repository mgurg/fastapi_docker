from uuid import UUID
from sqlalchemy import not_, select
from sqlalchemy.orm import Session
from collections.abc import Sequence
from app.models.models import PartUsed


def get_parts(db: Session, issue_id: UUID | None = None, is_hidden: bool | None = None) -> Sequence[PartUsed]:
    query = select(PartUsed).where(PartUsed.deleted_at.is_(None))

    if is_hidden is True:
        query = query.where(not_(PartUsed.is_hidden.is_(True)))

    if issue_id is not None:
        query = query.filter(PartUsed.issue_id == issue_id)

    # query = query.order_by(text(f"{sort_column} {sort_order}"))

    result = db.execute(query)

    return result.scalars().all()


def get_part_by_uuid(db: Session, uuid: UUID) -> PartUsed | None:
    query = select(PartUsed).where(PartUsed.uuid == uuid)

    result = db.execute(query)

    return result.scalar_one_or_none()


# def get_part_by_name(db: Session, name: str) -> Tag:
#     query = select(Tag).where(Tag.name == name).where(Tag.deleted_at.is_(None))

#     result = db.execute(query)

#     return result.scalar_one_or_none()


# def get_parts_id_by_uuid(db: Session, uuid: list[UUID]) -> Tag:
#     query = select(Tag.id).filter(Tag.uuid.in_(uuid))

#     result = db.execute(query)

#     return result.scalars().all()


def create_part(db: Session, data: dict) -> PartUsed:
    new_part = PartUsed(**data)
    db.add(new_part)
    db.commit()
    db.refresh(new_part)

    return new_part


def update_part(db: Session, db_part: PartUsed, update_data: dict) -> PartUsed:
    for key, value in update_data.items():
        setattr(db_part, key, value)

    db.add(db_part)
    db.commit()
    db.refresh(db_part)

    return db_part
