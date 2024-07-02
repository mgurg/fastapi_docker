from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import SettingNotification

UserDB = Annotated[Session, Depends(get_db)]


class SettingNotificationRepo(GenericRepo[SettingNotification]):
    def __init__(self, session: UserDB) -> None:
        self.Model = SettingNotification
        super().__init__(session, self.Model)

    def get_by_user_id(self, user_id: int) -> SettingNotification | None:
        query = select(self.Model).where(self.Model.user_id == user_id)

        result = self.session.execute(query)
        return result.scalar_one_or_none()
