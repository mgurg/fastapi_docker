from datetime import datetime, time, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.models import Event, Issue, Item, User


def get_issues_counter_summary(db: Session):
    # TODO: tylko dla dzisiaj

    date_from = datetime.combine(datetime.now(timezone.utc), time.min)

    query = select(Issue.status, func.count(Issue.status)).group_by(Issue.status)
    query = query.filter(func.DATE(Issue.created_at) >= date_from)

    result = db.execute(query)  # await db.execute(query)
    return result.all()


def get_issues_counter_by_status(db: Session, status: list):
    query = (
        select(Issue.author_id, func.count(Issue.author_id)).where(Issue.status.in_(status)).group_by(Issue.author_id)
    )

    result = db.execute(query)  # await db.execute(query)
    return result.all()


def get_items_counter_summary(db: Session):
    query = select(Item.author_id, func.count(Item.author_id)).group_by(Item.author_id)
    result = db.execute(query)  # await db.execute(query)
    return result.all()


def get_users_counter_summary(db: Session, user_id: int):
    query = select(func.count(User.id)).where(User.id != user_id)
    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_favourites_counter_summary(db: Session, user_id: int):
    query = select(func.count(Item.id)).filter(Item.users_item.any(User.id == user_id))

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_events(db: Session):
    query = select(Event.id, Event.action, Event.author_id)

    result = db.execute(query)  # await db.execute(query)

    return result.all()
