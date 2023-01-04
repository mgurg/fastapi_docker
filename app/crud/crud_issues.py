from uuid import UUID

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.models.models import Issue, User


def get_issues(db: Session, search: str, sort_column: str, sort_order: str) -> Issue:
    # return db.execute(select(Issue)).scalars().all()
    search_filters = []

    query = select(Issue).order_by(text(f"{sort_column} {sort_order}"))

    if search is not None:
        search_filters.append(Issue.name.ilike(f"%{search}%"))
        search_filters.append(Issue.text.ilike(f"%{search}%"))

        query = query.filter(or_(False, *search_filters))

    result = db.execute(query)  # await db.execute(query)

    return result.scalars().all()


def get_issues_by_user_id(db, user_id) -> Issue:
    query = select(Issue).filter(Issue.users_issue.any(User.id == user_id))

    result = db.execute(query)  # await db.execute(query)
    return result.scalars().all()


def get_issue_by_uuid(db: Session, uuid: UUID) -> Issue:
    query = select(Issue).where(Issue.uuid == uuid)

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_issue_summary(db: Session):
    # return db.execute(select(Issue.status, func.count(Issue.status)).group_by(Issue.status)).all()

    query = select(Issue.status, func.count(Issue.status)).group_by(Issue.status)

    result = db.execute(query)  # await db.execute(query)
    return result.all()


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
