from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session, selectinload

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Guide, Item

UserDB = Annotated[Session, Depends(get_db)]


class GuideRepo(GenericRepo[Guide]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Guide
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> Guide | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid)).options(selectinload("*"))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_guides(
        self,
        offset: int,
        limit: int,
        sort_column: str,
        sort_order: str,
        search: str | None = None,
        item_id: int | None = None,
    ) -> tuple[Sequence[Guide], int]:
        base_query = self.session.query(self.Model).filter(Guide.deleted_at.is_(None))

        if search:
            search_filter = or_(self.Model.name.ilike(f"%{search}%"), self.Model.text.ilike(f"%{search}%"))
            base_query = base_query.filter(search_filter)

        if item_id:
            item_filter = self.Model.item.any(Item.id == item_id)
            base_query = base_query.filter(item_filter)

        guides_query = base_query.order_by(text(f"{sort_column} {sort_order}")).offset(offset).limit(limit)
        result = self.session.execute(guides_query)

        count_query = base_query.with_entities(func.count(self.Model.id))
        count_result = self.session.execute(count_query)
        total_records = count_result.scalar_one_or_none() or 0

        return result.scalars().all(), total_records
