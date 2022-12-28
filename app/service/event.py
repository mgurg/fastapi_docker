from datetime import datetime, timezone
from uuid import uuid4

import pendulum
from sqlalchemy.orm import Session

from app.crud import crud_events, crud_items
from app.models.models import Issue, Item, User

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


def issue_create_new(db: Session, author: User, item: Item, issue: Issue, event_action: str, stat_entries: list):
    """Add event for newly created Issue"""

    event_data = {
        "uuid": str(uuid4()),
        "author_id": author.id,
        "author_name": f"{author.first_name} {author.last_name}",
        "resource": "item",
        "resource_uuid": item.uuid,
        "resource_id": item.id,
        "action": event_action,
        "created_at": datetime.now(timezone.utc),
        "description": issue.text,
    }

    new_event = crud_events.create_event(db, event_data)

    for entry in stat_entries:
        event_statistic = {
            "uuid": str(uuid4()),
            "item_uuid": item.uuid,
            "issue_uuid": issue.uuid,
            "action": entry,
            "date_from": datetime.now(timezone.utc),
            "date_to": None,
            "duration": None,
        }
        crud_events.create_event_statistic(db, event_statistic)


def issue_change_status(
    db: Session, author: User, item: Item, issue: Issue, event_action: str, prev_event_stat: str = None
):
    # if author is None:
    #     author_name = f"{db_user.first_name} {db_user.last_name}"

    event_data = {
        "uuid": str(uuid4()),
        "author_id": author.id,
        "author_name": f"{author.first_name} {author.last_name}",
        "resource": "item",
        "resource_uuid": item.uuid,
        "resource_id": item.id,
        "action": event_action,
        "created_at": datetime.now(timezone.utc),
    }

    new_event = crud_events.create_event(db, event_data)

    if prev_event_stat is not None:
        event = crud_events.get_statistics_by_issue_uuid_and_status(db, issue.uuid, prev_event_stat)

        if event is not None:
            dt = pendulum.parse(str(event.date_from))

        event_statistic_update = {
            "date_to": datetime.now(timezone.utc),
            "duration": dt.diff(pendulum.now("UTC")).in_seconds(),
        }
        crud_events.update_event(db, event, event_statistic_update)


def issue_reject_new(db: Session, author_id: int, item_id: int, issue: Issue):
    event_data = {
        "uuid": str(uuid4()),
        "author_id": author_id,
        "author_name": "author_name",
        "action": "issueRejected",
        "created_at": datetime.now(timezone.utc),
    }

    print("#################################")
    print(event_data)
    print("#################################")

    # new_event = crud_events.create_event(db, event_data)
    # crud_events.create_event_statistic(db, event_statistic_data)


def issue_assign_person(db: Session, author_id: int, item_id: int, issue: Issue):
    event_data = {
        "uuid": str(uuid4()),
        "author_id": author_id,
        "author_name": "author_name",
        "action": "issueAssignedPerson",
        "created_at": datetime.now(timezone.utc),
    }

    new_event = crud_events.create_event(db, event_data)


def issue_start_repair(db: Session, author_id: int, item_id: int, issue: Issue):
    event_data = {
        "uuid": str(uuid4()),
        "author_id": author_id,
        "author_name": "author_name",
        "action": "issueRepairStart",
        "created_at": datetime.now(timezone.utc),
    }

    new_event = crud_events.create_event(db, event_data)
    # crud_events.create_event_statistic(db, event_statistic_data)


def issue_pause_repair(db: Session, author_id: int, item_id: int, issue: Issue):
    event_data = {
        "uuid": str(uuid4()),
        "author_id": author_id,
        "author_name": "author_name",
        "action": "issueRepairPause",
        "created_at": datetime.now(timezone.utc),
    }

    new_event = crud_events.create_event(db, event_data)
    # crud_events.create_event_statistic(db, event_statistic_data)


def issue_continue_repair(db: Session, author_id: int, item_id: int, issue: Issue):
    event_data = {
        "uuid": str(uuid4()),
        "author_id": author_id,
        "author_name": "author_name",
        "action": "issueRepairContinue",
        "created_at": datetime.now(timezone.utc),
    }

    new_event = crud_events.create_event(db, event_data)
    # crud_events.create_event_statistic(db, event_statistic_data)


def issue_accept_repair(db: Session, author_id: int, item_id: int, issue: Issue):
    event_data = {
        "uuid": str(uuid4()),
        "author_id": author_id,
        "author_name": "author_name",
        "action": "issueRepairContinue",
        "created_at": datetime.now(timezone.utc),
    }

    new_event = crud_events.create_event(db, event_data)
    # crud_events.create_event_statistic(db, event_statistic_data)


def issue_reject_repair():
    ...


def issue_reopen_repair():
    ...
