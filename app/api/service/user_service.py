from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.api.repository.UserRepo import UserRepo
from app.models.models import User


class UserService:
    def __init__(self, user_repo: Annotated[UserRepo, Depends()]) -> None:
        self.user_repo = user_repo

    def get_user_by_uuid(self, uuid: UUID) -> User | None:
        db_user = self.user_repo.get_by_uuid(uuid)
        return db_user

    def get_users(self, sort_column: str, sort_order: str, search: str | None = None) -> list[User]:
        db_users = self.user_repo.get_users(sort_column, sort_order, search)

        return db_users
