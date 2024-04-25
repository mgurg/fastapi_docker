from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, Sequence, func, text
from sqlalchemy.orm import Session

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import User

UserDB = Annotated[Session, Depends(get_db)]


class UserRepo(GenericRepo[User]):
    def __init__(self, session: UserDB) -> None:
        self.Model = User
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> User | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid))  # .options(selectinload("*"))
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_users(self, sort_column: str, sort_order: str, search: str | None = None) -> Sequence[User]:
        query = (
            select(self.Model)
            .where(self.Model.deleted_at.is_(None))
            .where(self.Model.is_visible.is_(True))
            .order_by(text(f"{sort_column} {sort_order}"))
        )

        all_filters = []
        if search is not None:
            all_filters.append(func.concat(self.Model.first_name, " ", self.Model.last_name).ilike(f"%{search}%"))

            query = query.filter(*all_filters)

        result = self.session.execute(query)
        return result.scalars().all()
