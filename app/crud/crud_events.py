from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.models import Event, EventSummary


def get_event_time_statistics_by_item(db: Session, item_uuid: UUID):
    return (
        db.execute(
            select(EventSummary.action, func.sum(EventSummary.duration).label("time_duration"))
            .where(EventSummary.item_uuid == item_uuid)
            .group_by(EventSummary.action)
        )
        .scalars()
        .all()
    )


def get_event_time_statistics_by_issue(db: Session, issue_uuid: UUID):
    return (
        db.execute(
            select(EventSummary.action, func.sum(EventSummary.duration).label("time_duration"))
            .where(EventSummary.issue_uuid == issue_uuid)
            .group_by(EventSummary.action)
        )
        .scalars()
        .all()
    )


def get_statistics_by_issue_uuid_and_status(db: Session, issue_uuid: UUID, status: str) -> EventSummary:
    query = (
        select(EventSummary)
        .where(EventSummary.issue_uuid == issue_uuid)
        .where(EventSummary.action == status)
        .where(EventSummary.date_to == None)
    )
    return db.execute(query).scalar_one_or_none()


def get_events_by_uuid_and_resource(
    db: Session, resource_uuid: UUID, action: str = None, date_from=None, date_to=None
) -> Event:

    # .where(Event.created_at > date_from)
    # .where(Event.created_at < date_to)

    query = select(Event).where(Event.resource_uuid == resource_uuid).where(Event.resource == "item")

    if action is not None:
        query = query.where(Event.action == action)

    events_with_date = db.execute(query).scalars().all()

    return events_with_date


def get_events_by_thread(
    db: Session, thread_uuid: UUID, thread_resource: str = None, date_from=None, date_to=None
) -> Event:

    # .where(Event.created_at > date_from)
    # .where(Event.created_at < date_to)

    query = select(Event).where(Event.thread_uuid == thread_uuid)

    if thread_resource is not None:
        query = query.where(Event.thread_resource == thread_resource)

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
