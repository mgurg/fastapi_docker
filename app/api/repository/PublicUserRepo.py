from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.repository.generics import GenericRepo
from app.db import get_public_db
from app.models.shared_models import PublicUser

PublicUserDB = Annotated[Session, Depends(get_public_db)]


class PublicUserRepo(GenericRepo[PublicUser]):
    def __init__(self, session: PublicUserDB) -> None:
        self.Model = PublicUser
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> PublicUser | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid))

        result = self.session.execute(query)
        return result.scalar_one_or_none()
