from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import SettingUser

UserDB = Annotated[Session, Depends(get_db)]


class SettingUserRepo(GenericRepo[SettingUser]):
    def __init__(self, session: UserDB) -> None:
        self.Model = SettingUser
        super().__init__(session, self.Model)

    def get_general_settings_by_names(self, user_id: int, names: list[str]) -> Sequence[SettingUser]:
        query = select(self.Model).where(self.Model.user_id == user_id).where(SettingUser.name.in_(names))

        result = self.session.execute(query)

        return result.scalars().all()

    def get_user_setting_by_name(self, user_id: int, name: str) -> SettingUser | None:
        query = select(SettingUser).where(self.Model.user_id == user_id).where(self.Model.name == name)

        result = self.session.execute(query)

        return result.scalar_one_or_none()
