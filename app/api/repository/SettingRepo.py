from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Setting

UserDB = Annotated[Session, Depends(get_db)]


class SettingRepo(GenericRepo[Setting]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Setting
        super().__init__(session, self.Model)

    def get_by_names(self, uuid: UUID):
        query = select(self.Model).where(self.Model.uuid == str(uuid)).options(selectinload("*"))

        result = self.session.execute(query)
        return result.scalar_one_or_none()
