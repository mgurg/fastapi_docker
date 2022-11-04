from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.models import Guide


def get_guides(db: Session, search: str, sortColumn: str, sortOrder: str) -> Guide:
    return db.execute(select(Guide)).scalars().all()
    all_filters = []

    if search is not None:
        all_filters.append(func.concat(Guide.first_name, " ", Guide.last_name).ilike(f"%{search}%"))

    return db.execute(select(Guide).filter(*all_filters).order_by(text(f"{sortColumn} {sortOrder}"))).scalars().all()


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
