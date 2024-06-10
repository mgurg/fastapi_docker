from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session, selectinload

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Item, User

UserDB = Annotated[Session, Depends(get_db)]


class ItemRepo(GenericRepo[Item]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Item
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> Item | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid)).options(selectinload("*"))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_items(
            self,
            offset: int,
            limit: int,
            sort_column: str,
            sort_order: str,
            search: str | None = None,
            user_id: int | None = None,
    ) -> tuple[Sequence[Item], int]:
        base_query = self.session.query(self.Model).filter(self.Model.deleted_at.is_(None))

        if search:
            search_filter = or_(self.Model.name.ilike(f"%{search}%"), self.Model.text.ilike(f"%{search}%"))
            base_query = base_query.filter(search_filter)

        if user_id:
            user_filter = self.Model.users_item.any(User.id == user_id)
            base_query = base_query.filter(user_filter)

        items_query = base_query.order_by(text(f"{sort_column} {sort_order}")).offset(offset).limit(limit)
        result = self.session.execute(items_query)

        count_query = base_query.with_entities(func.count(self.Model.id))
        count_result = self.session.execute(count_query)
        total_records = count_result.scalar_one_or_none() or 0

        return result.scalars().all(), total_records

    def get_items_counter_summary(self):
        query = select(self.Model.author_id, func.count(self.Model.author_id)).group_by(self.Model.author_id)
        result = self.session.execute(query)
        return result.all()

    def get_favourites_counter_summary(self, user_id: int):
        query = select(func.count(self.Model.id)).filter(self.Model.users_item.any(User.id == user_id))

        result = self.session.execute(query)
        return result.scalar_one_or_none()
