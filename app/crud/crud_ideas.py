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


def get_idea_by_user_id(db: Session, author_id: int) -> Idea:
    return db.execute(select(Idea).where(Idea.author_id == author_id).where(Idea.deleted_at.is_(None))).scalars().all()


def create_idea(db: Session, data: dict) -> Idea:
    new_idea = Idea(**data)
    db.add(new_idea)
    db.commit()
    db.refresh(new_idea)

    return new_idea


def update_idea(db: Session, db_idea: Idea, update_data: dict) -> Idea:
    for key, value in update_data.items():
        setattr(db_idea, key, value)

    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)

    return db_idea
