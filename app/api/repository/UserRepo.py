from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Sequence, func, select, text
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

    def get_users(
        self, offset: int, limit: int, sort_column: str, sort_order: str, search: str | None = None
    ) -> tuple[Sequence[User], int]:
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

        result = self.session.execute(query.offset(offset).limit(limit))

        total_records: int = 0
        try:
            count_statement = (
                select(func.count(self.Model.id))
                .where(self.Model.deleted_at.is_(None))
                .where(self.Model.is_visible.is_(True))
            )
            count_result = self.session.execute(count_statement)
            counter = count_result.scalar_one_or_none()
            if counter:
                total_records = counter

        except Exception as e:
            print(e)

        return result.scalars().all(), total_records
