from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, text, func
from sqlalchemy.orm import Session

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Tag

UserDB = Annotated[Session, Depends(get_db)]


class TagRepo(GenericRepo[Tag]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Tag
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> Tag | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid))  # .options(selectinload("*"))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_by_name(self, name: str) -> Tag | None:
        query = select(self.Model).where(self.Model.name == name)

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_tags(self, offset: int, limit: int, sort_column: str, sort_order: str, is_hidden: bool | None = None):
        base_query = select(Tag).where(Tag.deleted_at.is_(None))

        if is_hidden is True:
            base_query = base_query.where(Tag.is_hidden.is_(True))

        query = base_query.order_by(text(f"{sort_column} {sort_order}")).offset(offset).limit(limit)

        result = self.session.execute(query)

        count_query = base_query.with_only_columns([func.count()]).order_by(None)
        total_records = self.session.execute(count_query).scalar_one_or_none() or 0

        return result.scalars().all(), total_records
