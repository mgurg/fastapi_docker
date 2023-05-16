from uuid import UUID

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session
from collections.abc import Sequence
from app.models.models import Item, User


def get_items(
    db: Session, sort_column: str, sort_order: str, search: str | None = None, user_id: int | None = None
) -> Sequence[Item]:
    query = select(Item)

    search_filters = []
    if search is not None:
        search_filters.append(Item.name.ilike(f"%{search}%"))
        search_filters.append(Item.text.ilike(f"%{search}%"))

        query = query.filter(or_(False, *search_filters))

    if user_id is not None:
        query = query.filter(Item.users_item.any(User.id == user_id))

    query = query.order_by(text(f"{sort_column} {sort_order}"))

    result = db.execute(query)  # await db.execute(query)

    return result.scalars().all()


def get_item_by_uuid(db: Session, uuid: UUID) -> Item | None:
    query = select(Item).where(Item.uuid == uuid)

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_item_by_id(db: Session, id: int) -> Item:
    query = select(Item).where(Item.id == id)

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


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
