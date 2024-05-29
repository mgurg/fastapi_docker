from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Item, User
from sqlalchemy import Select, or_, select, text

UserDB = Annotated[Session, Depends(get_db)]


class ItemRepo(GenericRepo[Item]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Item
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> Item | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid)).options(selectinload("*"))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_items(self, offset: int, limit: int, sort_column: str, sort_order: str, search: str | None = None,
                  user_id: int | None = None):
        query = select(Item).where(Item.deleted_at.is_(None))

        search_filters = []
        if search is not None:
            search_filters.append(Item.name.ilike(f"%{search}%"))
            search_filters.append(Item.text.ilike(f"%{search}%"))

            query = query.filter(or_(False, *search_filters))

        if user_id is not None:
            query = query.filter(Item.users_item.any(User.id == user_id))

        query = query.order_by(text(f"{sort_column} {sort_order}"))
        result = self.session.execute(query.offset(offset).limit(limit))

        total_records: int = 0
        count_statement = (
            select(func.count(self.Model.id))
            .where(self.Model.deleted_at.is_(None))
        )
        if search is not None:
            count_statement = count_statement.filter(or_(False, *search_filters))

        if user_id is not None:
            count_statement = count_statement.filter(Item.users_item.any(User.id == user_id))

        count_result = self.session.execute(count_statement)
        counter = count_result.scalar_one_or_none()
        if counter:
            total_records = counter

        return result.scalars().all(), total_records

    def get_items_counter_summary(self):
        query = select(self.Model.author_id, func.count(self.Model.author_id)).group_by(self.Model.author_id)
        result = self.session.execute(query)
        return result.all()

    def get_favourites_counter_summary(self, user_id: int):
        query = select(func.count(self.Model.id)).filter(self.Model.users_item.any(User.id == user_id))

        result = self.session.execute(query)
        return result.scalar_one_or_none()
