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
