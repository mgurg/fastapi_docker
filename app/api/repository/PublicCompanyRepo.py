from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.repository.generics import GenericRepo
from app.db import get_public_db
from app.models.shared_models import PublicCompany

# UserDB = Annotated[Session, Depends(get_db)]

PublicUserDB = Annotated[Session, Depends(get_public_db)]


class PublicCompanyRepo(GenericRepo[PublicCompany]):
    def __init__(self, session: PublicUserDB) -> None:
        self.Model = PublicCompany
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> PublicCompany | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_by_nip(self, nip: str) -> PublicCompany | None:
        query = select(self.Model).where(self.Model.nip == nip)

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_users_count(self) -> int | None:
        query = select(func.count(self.Model.id))

        result = self.session.execute(query)  # await db.execute(query)
        return result.scalar_one_or_none()
