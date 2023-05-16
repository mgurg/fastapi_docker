from uuid import UUID

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session
from collections.abc import Sequence
from app.models.models import Guide, Item


def get_guides(db: Session, search: str, item_id: int, sort_column: str, sort_order: str) -> Sequence[Guide]:
    query = select(Guide)

    search_filters = []
    if search is not None:
        search_filters.append(Guide.name.ilike(f"%{search}%"))
        search_filters.append(Guide.text.ilike(f"%{search}%"))

        query = query.filter(or_(False, *search_filters))

    if item_id is not None:
        query = query.filter(Guide.item.any(Item.id == item_id))

    query = query.order_by(text(f"{sort_column} {sort_order}"))

    result = db.execute(query)  # await db.execute(query)

    return result.scalars().all()


def get_guide_by_uuid(db: Session, uuid: UUID) -> Guide:
    return db.execute(select(Guide).where(Guide.uuid == uuid)).scalar_one_or_none()


def create_guide(db: Session, data: dict) -> Guide:
    new_guide = Guide(**data)
    db.add(new_guide)
    db.commit()
    db.refresh(new_guide)

    return new_guide


def update_guide(db: Session, db_guide: Guide, update_data: dict) -> Guide:
    for key, value in update_data.items():
        setattr(db_guide, key, value)

    db.add(db_guide)
    db.commit()
    db.refresh(db_guide)

    return db_guide
