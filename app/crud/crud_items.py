from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.models import Item


def get_items(db: Session, search: str, sortColumn: str, sortOrder: str) -> Item:
    return db.execute(select(Item)).scalars().all()
    all_filters = []

    if search is not None:
        all_filters.append(func.concat(Item.first_name, " ", Item.last_name).ilike(f"%{search}%"))

    return db.execute(select(Item).filter(*all_filters).order_by(text(f"{sortColumn} {sortOrder}"))).scalars().all()


def get_item_by_uuid(db: Session, uuid: UUID) -> Item:
    return db.execute(select(Item).where(Item.uuid == uuid)).scalar_one_or_none()


def create_item(db: Session, data: dict) -> Item:
    new_item = Item(**data)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


def update_item(db: Session, db_item: Item, update_data: dict) -> Item:
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item
