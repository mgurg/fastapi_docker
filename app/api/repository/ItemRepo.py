from datetime import datetime, timezone, time
from typing import Annotated, Any, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select, Row
from sqlalchemy.orm import Session, selectinload

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Role, Issue, Item, User

UserDB = Annotated[Session, Depends(get_db)]


class ItemRepo(GenericRepo[Item]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Item
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> Item | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid)).options(selectinload("*"))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_items_counter_summary(self):
        query = select(self.Model.author_id, func.count(self.Model.author_id)).group_by(self.Model.author_id)
        result = self.session.execute(query)
        return result.all()


    def get_favourites_counter_summary(self, user_id: int):
        query = select(func.count(self.Model.id)).filter(self.Model.users_item.any(User.id == user_id))

        result = self.session.execute(query)
        return result.scalar_one_or_none()