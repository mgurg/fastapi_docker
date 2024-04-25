from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
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
