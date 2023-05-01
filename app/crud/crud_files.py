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


def get_orphaned_files(db: Session) -> list[UUID]:
    files_guides = db.execute(select(File.id).filter(File.guide.any())).scalars().all()
    files_items = db.execute(select(File.id).filter(File.item.any())).scalars().all()
    files_ideas = db.execute(select(File.id).filter(File.idea.any())).scalars().all()

    files_with_relations = list(set(files_guides + files_items + files_ideas))

    files_without_relations = db.execute(select(File.uuid).where(File.id.not_in(files_with_relations))).scalars().all()
    # for f in files_guides:
    #     print(f.id)
    # files_guides = db.execute(select(file_guide_rel)).scalars().all()
    # files_items = db.execute(select(file_item_rel)).scalars().all()
    # files_ideas = db.execute(select(file_idea_rel)).scalars().all()
    #
    return files_without_relations


def get_files_size_in_db(db: Session) -> int:
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
