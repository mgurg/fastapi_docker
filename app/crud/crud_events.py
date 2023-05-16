from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session
from collections.abc import Sequence

from app.models.models import Event, EventSummary


def get_event_time_statistics_by_item(db: Session, item_uuid: UUID):
    return db.execute(
        select(EventSummary.action, func.sum(EventSummary.duration).label("time_duration"))
        .where(EventSummary.resource == "item")
        .where(EventSummary.resource_uuid == item_uuid)
        .group_by(EventSummary.action)
    ).all()


def get_event_time_statistics_by_issue(db: Session, issue_uuid: UUID):
    return db.execute(
        select(EventSummary.action, func.sum(EventSummary.duration).label("time_duration"))
        .where(EventSummary.issue_uuid == issue_uuid)
        .group_by(EventSummary.action)
    ).all()


def get_statistics_by_issue_uuid_and_status(db: Session, issue_uuid: UUID, status: str) -> EventSummary | None:
    query = (
        select(EventSummary)
        .where(EventSummary.issue_uuid == issue_uuid)
        .where(EventSummary.action == status)
        .where(EventSummary.date_to.is_(None))
    )
    return db.execute(query).scalar_one_or_none()


def get_event_summary_by_resource_uuid_and_status(
    db: Session, resource: str, resource_uuid: UUID, status: str, internal_value: str | None = None
) -> EventSummary | None:
    query = (
        select(EventSummary)
        .where(EventSummary.resource == resource)
        .where(EventSummary.resource_uuid == resource_uuid)
        .where(EventSummary.action == status)
        .where(EventSummary.date_to.is_(None))
    )

    if internal_value is not None:
        query = query.where(EventSummary.internal_value == internal_value)

    result = db.execute(query)  # await db.execute(query)

    return result.scalar_one_or_none()


def get_basic_summary_users_uuids(db: Session, resource: str, resource_uuid: UUID, action: str) -> list[UUID]:
    query = (
        select(distinct(EventSummary.internal_value))
        .where(EventSummary.resource == resource)
        .where(EventSummary.resource_uuid == resource_uuid)
        .where(EventSummary.action == action)
    )

    result = db.execute(query)
    return result.scalars().all()


def get_events_by_uuid_and_resource(
    db: Session, resource_uuid: UUID, action: str = None, date_from=None, date_to=None
) -> Sequence[Event]:
    # .where(Event.created_at > date_from)
    # .where(Event.created_at < date_to)

    query = select(Event).where(Event.resource_uuid == resource_uuid).where(Event.resource == "item")

    if action is not None:
        query = query.where(Event.action == action)

    result = db.execute(query)  # await db.execute(query)
    events_with_date = result.scalars().all()

    return events_with_date


def get_event_status_list(db: Session, resource: str, resource_uuid: UUID):
    query = select(Event.action).where(Event.resource_uuid == resource_uuid).where(Event.resource == resource)

    result = db.execute(query)  # await db.execute(query)
    event_actions = result.scalars().all()

    return event_actions


def get_events_for_issue_summary(db: Session, resource: str, resource_uuid: UUID):
    query = (
        select(
            EventSummary.action,
            func.sum(EventSummary.duration).label("time_duration"),
            func.count(EventSummary.action).label("total"),
        )
        .where(EventSummary.resource == resource)
        .where(EventSummary.resource_uuid == resource_uuid)
        .group_by(EventSummary.action)
    )

    result = db.execute(query)  # await db.execute(query)
    events_with_date = result.all()

    return events_with_date


def get_events_user_issue_summary(db: Session, resource: str, resource_uuid: UUID, user_uuid: list[UUID]):
    query = (
        select(
            EventSummary.internal_value,
            func.sum(EventSummary.duration).label("time_duration"),
            func.count(EventSummary.internal_value).label("total"),
        )
        .where(EventSummary.action == "issueUserActivity")
        .where(EventSummary.resource == resource)
        .where(EventSummary.resource_uuid == resource_uuid)
        .where(EventSummary.internal_value.in_(user_uuid))
        .group_by(EventSummary.internal_value)
    )

    result = db.execute(query)  # await db.execute(query)
    events_with_date = result.all()

    return events_with_date


def get_events_by_thread(db: Session, resource_uuid: UUID, resource: str = None, date_from=None, date_to=None) -> Event:
    # .where(Event.created_at > date_from)
    # .where(Event.created_at < date_to)

    query = select(Event).where(Event.resource == resource)
    query = query.where(Event.resource_uuid == resource_uuid)

    events_with_date = db.execute(query).scalars().all()

    return events_with_date


def create_event(db: Session, data: dict) -> Event:
    new_event = Event(**data)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


def create_event_statistic(db: Session, data: dict) -> EventSummary:
    new_event_statistics = EventSummary(**data)
    db.add(new_event_statistics)
    db.commit()
    db.refresh(new_event_statistics)

    return new_event_statistics


def update_event(db: Session, db_event: EventSummary, update_data: dict) -> EventSummary:
    for key, value in update_data.items():
        setattr(db_event, key, value)

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event
