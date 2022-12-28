from uuid import UUID

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

from app.models.models import Event, EventStatistic


def get_statistics_by_issue_uuid_and_status(db: Session, issue_uuid: UUID, status: str) -> EventStatistic:
    return db.execute(
        select(EventStatistic)
        .where(EventStatistic.issue_uuid == issue_uuid)
        .where(EventStatistic.action == status)
        .where(EventStatistic.date_to == None)
    ).scalar_one_or_none()


def get_events_by_uuid_and_resource(
    db: Session, resource_uuid: UUID, resource: str, date_from=None, date_to=None
) -> Event:

    # .where(Event.created_at > date_from)
    # .where(Event.created_at < date_to)

    print("######################")
    print(resource_uuid, resource)
    events_with_date = (
        db.execute(select(Event).where(Event.resource_uuid == resource_uuid).where(Event.resource == resource))
        .scalars()
        .all()
    )

    return events_with_date


def create_event(db: Session, data: dict) -> Event:
    new_event = Event(**data)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


def create_event_statistic(db: Session, data: dict) -> EventStatistic:
    new_event_statistics = EventStatistic(**data)
    db.add(new_event_statistics)
    db.commit()
    db.refresh(new_event_statistics)

    return new_event_statistics


def update_event(db: Session, db_event: EventStatistic, update_data: dict) -> EventStatistic:
    for key, value in update_data.items():
        setattr(db_event, key, value)

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event
