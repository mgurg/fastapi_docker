from datetime import datetime, timezone
from uuid import uuid4

import pendulum
from sqlalchemy.orm import Session

from app.crud import crud_events, crud_users
from app.models.models import Event, Issue, Item, User

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


def create_new_event(
    db: Session, author: User, item: Item, issue: Issue, action: str, description: str = None, value: str = None
) -> Event:

    if description is None:
        match action:
            case "issueAccepted":
                description = "Issue accepted"
            case "issueRejected":
                description = "Issue rejected"
            case "issueRepairPause":
                description = "Issue paused"
            case "issueRepairFinish":
                description = "Issue resolved"

    if description == "issueChangeAssignedPerson" and description == "added":
        description = "New person assigned to issue"
        person = crud_users.get_user_by_uuid(value)
        if person is not None:
            value = person.first_name + " " + person.last_name

    if description == "issueChangeAssignedPerson" and description == "removed":
        description = "Person removed from issue"
        person = crud_users.get_user_by_uuid(value)
        if person is not None:
            value = person.first_name + " " + person.last_name

    event_data = {
        "uuid": str(uuid4()),
        "author_id": author.id,
        "author_uuid": author.uuid,
        "author_name": f"{author.first_name} {author.last_name}",
        "resource": "item",
        "resource_id": item.id,
        "resource_uuid": item.uuid,
        "action": action,
        "description": description,
        "value": value,
        "created_at": datetime.now(timezone.utc),
    }

    new_event = crud_events.create_event(db, event_data)
    return new_event


def create_new_event_statistic(db: Session, item: Item, issue: Issue, action: str):
    event_statistic = {
        "uuid": str(uuid4()),
        "resource": "item",
        "resource_uuid": item.uuid,
        "issue_uuid": issue.uuid,
        "action": action,
        "date_from": datetime.now(timezone.utc),
        "date_to": None,
        "duration": None,
        "created_at": datetime.now(timezone.utc),
    }
    new_event_statistics = crud_events.create_event_statistic(db, event_statistic)
    return new_event_statistics


def close_event_statistics(db: Session, issue: Issue, previous_event: str):
    event = crud_events.get_statistics_by_issue_uuid_and_status(db, issue.uuid, previous_event)

    if event is not None:
        dt = pendulum.parse(str(event.date_from))
        time_diff = dt.diff(pendulum.now("UTC")).in_seconds()

        event_statistic_update = {"date_to": datetime.now(timezone.utc), "duration": time_diff}
        event = crud_events.update_event(db, event, event_statistic_update)

    return event
