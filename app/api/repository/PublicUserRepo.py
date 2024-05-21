from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import EmailStr
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

    def get_by_email(self, email: EmailStr) -> PublicUser | None:
        query = select(self.Model).where(self.Model.email == email)

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_by_service_token(self, token: str) -> PublicUser | None:
        query = (
            select(self.Model)
            .where(self.Model.service_token == token)
            .where(self.Model.is_active == True)
            .where(self.Model.service_token_valid_to > datetime.now(timezone.utc))
        )

        result = self.session.execute(query)
        return result.scalar_one_or_none()
