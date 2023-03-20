from datetime import datetime
from uuid import UUID

from sqlalchemy import Date, distinct, extract, func, not_, or_, select, text
from sqlalchemy.orm import Session

from app.models.models import EventSummary, Issue, Tag, User


def get_issues(
    db: Session,
    search: str | None,
    status: str | None,
    user_id: int | None,
    priority: str | None,
    sort_column: str,
    sort_order: str,
    date_from: datetime = None,
    date_to: datetime = None,
    tags: list[int] = None,
) -> Issue:
    search_filters = []

    query = select(Issue)

    if search is not None:
        search_filters.append(Issue.name.ilike(f"%{search}%"))
        search_filters.append(Issue.text.ilike(f"%{search}%"))

        query = query.filter(or_(False, *search_filters))

    match status:
        case "all":
            ...
        case "active":
            query = query.where(not_(Issue.status.in_(["done", "rejected"])))
        case "inactive":
            query = query.where(Issue.status.in_(["done", "rejected"]))
        case "new" | "accepted" | "rejected" | "in_progress" | "paused" | "done" as issue_status:
            query = query.where(Issue.status == issue_status)

    match priority:
        case "low":
            query = query.where(Issue.priority == "10")
        case "medium":
            query = query.where(Issue.priority == "20")
        case "high":
            query = query.where(Issue.priority == "30")
        case _:
            ...

    if user_id is not None:
        query = query.filter(Issue.users_issue.any(User.id == user_id))

    if date_from is not None:
        query = query.filter(func.DATE(Issue.created_at) >= date_from)

    if date_to is not None:
        query = query.filter(func.DATE(Issue.created_at) <= date_to)

    if tags is not None:
        query = query.where((Issue.tags_issue.any(Tag.id.in_(tags))))

    query = query.order_by(text(f"{sort_column} {sort_order}"))

    result = db.execute(query)  # await db.execute(query)

    return result.scalars().all()


def get_last_issue_id(db):
    query = select(Issue.id).order_by(Issue.id.desc()).limit(1)

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_issue_by_uuid(db: Session, uuid: UUID) -> Issue:
    query = select(Issue).where(Issue.uuid == uuid)

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def count_issues_by_tag(db: Session, tag_id: int):
    query = select(func.count(Issue.id)).filter(Issue.tags_issue.any(Tag.id == tag_id))

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


# --- STATS ---
def get_item_issues_uuids(db, item_id: int) -> list[UUID]:
    query = select(Issue.uuid).where(Issue.item_id == item_id)

    result = db.execute(query)  # await db.execute(query)

    return result.scalars().all()


def get_item_issues_ids(db, item_id: int) -> list[int]:
    query = select(Issue.id).where(Issue.item_id == item_id)

    result = db.execute(query)  # await db.execute(query)

    return result.scalars().all()


def get_item_issues_by_day(db, item_ids: list[int]):
    query = (
        select(Issue.created_at.cast(Date).label("date"), func.count(distinct(Issue.id)))
        .where(Issue.item_id.in_(item_ids))
        .group_by("date")
    )

    result = db.execute(query)  # await db.execute(query)

    return result.all()


def get_issues_by_day(db, date_from: datetime = None, date_to: datetime = None):
    query = select(Issue.created_at.cast(Date).label("date"), func.count(distinct(Issue.id)))

    if date_from is not None:
        query = query.filter(func.DATE(Issue.created_at) >= date_from)

    if date_to is not None:
        query = query.filter(func.DATE(Issue.created_at) <= date_to)

    query = query.group_by("date")

    result = db.execute(query)  # await db.execute(query)

    return result.all()


def get_item_issues_by_hour(db, item_ids: list[int]):
    query = (
        select(extract("hour", Issue.created_at).label("hour"), func.count(distinct(Issue.id)))
        .where(Issue.item_id.in_(item_ids))
        .group_by("hour")
    )

    result = db.execute(query)  # await db.execute(query)

    return result.all()


def get_issues_by_hour(db, date_from: datetime = None, date_to: datetime = None):
    query = select(extract("hour", Issue.created_at).label("hour"), func.count(distinct(Issue.id)))

    if date_from is not None:
        query = query.filter(func.DATE(Issue.created_at) >= date_from)

    if date_to is not None:
        query = query.filter(func.DATE(Issue.created_at) <= date_to)

    query = query.group_by("hour")

    result = db.execute(query)  # await db.execute(query)

    return result.all()


def get_item_issues_status(db, item_ids: list[int]):
    query = (
        select(Issue.status.label("status"), func.count(distinct(Issue.id)))
        .where(Issue.item_id.in_(item_ids))
        .group_by("status")
    )

    result = db.execute(query)  # await db.execute(query)

    return result.all()


def get_issues_status(db, date_from: datetime = None, date_to: datetime = None):
    query = select(Issue.status.label("status"), func.count(distinct(Issue.id)))

    if date_from is not None:
        query = query.filter(func.DATE(Issue.created_at) >= date_from)

    if date_to is not None:
        query = query.filter(func.DATE(Issue.created_at) <= date_to)

    query = query.group_by("status")

    result = db.execute(query)  # await db.execute(query)

    return result.all()


def get_mode_action_time(db, issues_uuids: list[UUID], action: str):
    query = (
        select(func.max(EventSummary.duration), func.avg(EventSummary.duration), func.min(EventSummary.duration))
        .where(EventSummary.resource_uuid.in_(issues_uuids))
        .where(EventSummary.resource == "issue")
        .where(EventSummary.action == action)
    )

    result = db.execute(query)  # await db.execute(query)

    return result.all()


def get_assigned_users(db, issues_uuids: list[UUID]):
    query = (
        select(distinct(EventSummary.internal_value))
        .where(EventSummary.resource_uuid.in_(issues_uuids))
        .where(EventSummary.resource == "issue")
        .where(EventSummary.action == "issueUserActivity")
    )

    result = db.execute(query)  # await db.execute(query)

    return result.all()


# --- STATS ---

# def get_issue_summary(db: Session):
#     # return db.execute(select(Issue.status, func.count(Issue.status)).group_by(Issue.status)).all()

#     query = select(Issue.status, func.count(Issue.status)).group_by(Issue.status)

#     result = db.execute(query)  # await db.execute(query)
#     return result.all()


def create_issue(db: Session, data: dict) -> Issue:
    new_issue = Issue(**data)
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return new_issue


def update_issue(db: Session, db_issue: Issue, update_data: dict) -> Issue:
    for key, value in update_data.items():
        setattr(db_issue, key, value)

    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)

    return db_issue
