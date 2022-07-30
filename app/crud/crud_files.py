from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import File

# def get_users(db: Session, skip: int = 0, limit: int = 100) -> User:
#     return db.execute(select(File).offset(skip).limit(limit)).scalars().all()
