from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Permission, Role

UserDB = Annotated[Session, Depends(get_db)]


class PermissionRepo(GenericRepo[Role]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Permission
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> Permission | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid)).options(selectinload("*"))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_role_by_name(self, name: str) -> Permission | None:
        query = select(self.Model).where(func.lower(self.Model.role_title) == name.lower())

        result = self.session.execute(query)
        return result.scalar_one_or_none()
