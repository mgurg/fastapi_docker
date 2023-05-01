from datetime import datetime, timezone
from uuid import UUID, uuid4

import pendulum
from sqlalchemy.orm import Session

from app.crud import crud_events
from app.models.models import Event, EventSummary, Issue, User

# OPEN (start)
# REJECT (?)
# IN-PROGRESS (resolve)
# PAUSED (?)
# RESOLVED (close)
# UNDER REVIEW (?)
# CLOSED (reopen)
# REOPEN (start)

# Status – where the issue is (for example, “In Progress” or “Under Review”)
# Resolution – why the issue is no longer in flight (for example, because it’s completed)


def create_new_basic_event(
    db: Session,
    author: User,
    issue: Issue,
    action: str,
    description: str | None = None,
    internal_value: str | None = None,
) -> Event:
    author_id = None
    author_uuid = None
    author_name = "anonymous"

    if author is not None:
        author_id = author.id
        author_uuid = author.uuid
        author_name = f"{author.first_name} {author.last_name}"

    resource_id = None
    resource_uuid = None
    if issue is not None:
        resource_id = issue.id
        resource_uuid = issue.uuid

    event_data = {
        "uuid": str(uuid4()),
        "author_id": author_id,
        "author_uuid": author_uuid,
        "author_name": author_name,
        "resource": "issue",
        "resource_id": resource_id,
        "resource_uuid": resource_uuid,
        "action": action,
        # "title": title,
        "description": description,
        "internal_value": internal_value,
        "created_at": datetime.now(timezone.utc),
    }

    new_event = crud_events.create_event(db, event_data)
    return new_event


def open_new_basic_summary(
    db: Session, resource: str, resource_uuid: UUID, action: str, internal_value: str | None = None
) -> EventSummary:
    event_statistic = {
        "uuid": str(uuid4()),
        "resource": resource,
        "resource_uuid": resource_uuid,
        "action": action,
        "internal_value": internal_value,
        "date_from": datetime.now(timezone.utc),
        "date_to": None,
        "duration": None,
        "created_at": datetime.now(timezone.utc),
    }
    new_event_statistics = crud_events.create_event_statistic(db, event_statistic)
    return new_event_statistics


def close_new_basic_summary(
    db: Session, resource: str, resource_uuid: UUID, previous_event: str, internal_value: str | UUID | None = None
):
    event = crud_events.get_event_summary_by_resource_uuid_and_status(
        db, resource, resource_uuid, previous_event, internal_value
    )

    if event is not None:
        dt = pendulum.parse(str(event.date_from))
        time_diff = dt.diff(pendulum.now("UTC")).in_seconds()

        event_statistic_update = {"date_to": datetime.now(timezone.utc), "duration": time_diff}
        event = crud_events.update_event(db, event, event_statistic_update)

    return event


# def create_new_item_event(
#     db: Session,
#     author: User,
#     item: Item,
#     issue: Issue,
#     action: str,
#     name: str,
#     description: str | None = None,
#     value: str | None = None,
# ) -> Event:
#     if action == "issue_change_assigned_person" and description == "added":
#         # description = "New person assigned to issue"
#         person = crud_users.get_user_by_uuid(db, value)
#         if person is not None:
#             value = person.first_name + " " + person.last_name

#     if action == "issue_change_assigned_person" and description == "removed":
#         # description = "Person removed from issue"
#         person = crud_users.get_user_by_uuid(db, value)
#         if person is not None:
#             value = person.first_name + " " + person.last_name

#     author_id = None
#     author_uuid = None
#     author_name = "anonymous"
#     if author is not None:
#         author_id = author.id
#         author_uuid = author.uuid
#         author_name = f"{author.first_name} {author.last_name}"

#     resource_id = None
#     resource_uuid = None
#     if item is not None:
#         resource_id = item.id
#         resource_uuid = item.uuid

#     event_data = {
#         "uuid": str(uuid4()),
#         "author_id": author_id,
#         "author_uuid": author_uuid,
#         "author_name": author_name,
#         "resource": "item",
#         "resource_id": resource_id,
#         "resource_uuid": resource_uuid,
#         "thread_uuid": issue.uuid,
#         "thread_resource": "issue",
#         "action": action,
#         "name": name,
#         "description": description,
#         "value": value,
#         "created_at": datetime.now(timezone.utc),
#     }

#     new_event = crud_events.create_event(db, event_data)
#     return new_event


# def create_new_item_event_statistic(db: Session, item: Item, issue: Issue, action: str):
#     resource_uuid = None
#     if item is not None:
#         resource_uuid = item.uuid

#     event_statistic = {
#         "uuid": str(uuid4()),
#         "resource": "item",
#         "resource_uuid": resource_uuid,
#         "issue_uuid": issue.uuid,
#         "action": action,
#         "date_from": datetime.now(timezone.utc),
#         "date_to": None,
#         "duration": None,
#         "created_at": datetime.now(timezone.utc),
#     }
#     new_event_statistics = crud_events.create_event_statistic(db, event_statistic)
#     return new_event_statistics


# def close_event_statistics(db: Session, issue: Issue, previous_event: str):
#     event = crud_events.get_statistics_by_issue_uuid_and_status(db, issue.uuid, previous_event)

#     if event is not None:
#         dt = pendulum.parse(str(event.date_from))
#         time_diff = dt.diff(pendulum.now("UTC")).in_seconds()

#         event_statistic_update = {"date_to": datetime.now(timezone.utc), "duration": time_diff}
#         event = crud_events.update_event(db, event, event_statistic_update)

#     return event
