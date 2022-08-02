from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.models import Idea


def get_ideas(db: Session, filters: list, sortColumn: str, sortOrder: str) -> Idea:
    return (
        db.execute(
            select(Idea).where(Idea.deleted_at.is_(None)).filter(*filters).order_by(text(f"{sortColumn} {sortOrder}"))
        )
        .scalars()
        .all()
    )


def get_idea_by_uuid(db: Session, uuid: UUID) -> Idea:
    return db.execute(select(Idea).where(Idea.uuid == uuid).where(Idea.deleted_at.is_(None))).scalar_one_or_none()


def create_idea(db: Session, data: dict) -> Idea:
    new_idea = Idea(**data)
    db.add(new_idea)
    db.commit()
    db.refresh(new_idea)

    return new_idea
