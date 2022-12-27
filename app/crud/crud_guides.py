from uuid import UUID

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

from app.models.models import Guide, Item


def get_guides(db: Session, search: str, sortColumn: str, sortOrder: str) -> Guide:
    search_filters = []
    if search is not None:
        search_filters.append(Guide.name.ilike(f"%{search}%"))
        search_filters.append(Guide.text.ilike(f"%{search}%"))

        return (
            db.execute(select(Guide).filter(or_(False, *search_filters)).order_by(text(f"{sortColumn} {sortOrder}")))
            .scalars()
            .all()
        )

    return db.execute(select(Guide).order_by(text(f"{sortColumn} {sortOrder}"))).scalars().all()


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


def get_guide_by_item_id(db, item_id):
    return db.execute(select(Guide).filter(Guide.item.any(Item.id == item_id))).scalars().all()
