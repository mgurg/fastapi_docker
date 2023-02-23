from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.shared_models import PublicCompany


def get_public_companies(db: Session) -> list[PublicCompany] | None:
    return db.execute(select(PublicCompany)).scalars().all()
