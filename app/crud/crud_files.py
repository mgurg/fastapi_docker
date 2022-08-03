from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.models import File


def get_files(db: Session) -> File:
    return db.execute(select(File).where(File.deleted_at.is_(None))).scalars().all()


def get_file_by_uuid(db: Session, uuid: UUID) -> File:
    return db.execute(select(File).where(File.uuid == uuid).where(File.deleted_at.is_(None))).scalar_one_or_none()


def get_file_by_id(db: Session, id: int) -> File:
    return db.execute(select(File).where(File.id == id).where(File.deleted_at.is_(None))).scalar_one()


def get_files_size_in_db(db: Session) -> File:
    db_size = db.execute(select(func.sum(File.size))).scalar_one_or_none()
    if not db_size:
        return 0
    return db_size


def create_file(db: Session, data: dict) -> File:
    new_file = File(**data)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return new_file
