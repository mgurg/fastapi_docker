from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Tag


def get_tags(db: Session) -> Tag:
    return db.execute(select(Tag).where(Tag.deleted_at.is_(None))).scalars().all()
