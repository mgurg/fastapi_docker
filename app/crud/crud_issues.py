from uuid import UUID

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

from app.models.models import Issue


def get_issues(db: Session, search: str, sortColumn: str, sortOrder: str) -> Issue:
    # return db.execute(select(Issue)).scalars().all()
    search_filters = []
    if search is not None:
        search_filters.append(Issue.name.ilike(f"%{search}%"))
        search_filters.append(Issue.text.ilike(f"%{search}%"))

        return (
            db.execute(select(Issue).filter(or_(False, *search_filters)).order_by(text(f"{sortColumn} {sortOrder}")))
            .scalars()
            .all()
        )

    return db.execute(select(Issue).order_by(text(f"{sortColumn} {sortOrder}"))).scalars().all()


def get_issue_by_uuid(db: Session, uuid: UUID) -> Issue:
    return db.execute(select(Issue).where(Issue.uuid == uuid)).scalar_one_or_none()


def create_issue(db: Session, data: dict) -> Issue:
    new_issue = Issue(**data)
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return new_issue


def update_issue(db: Session, db_issue: Issue, update_data: dict) -> Issue:
    for key, value in update_data.issues():
        setattr(db_issue, key, value)

    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)

    return db_issue
