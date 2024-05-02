from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Sequence

from app.api.repository.UserRepo import UserRepo
from app.models.models import User


class UserService:
    def __init__(self, user_repo: Annotated[UserRepo, Depends()]) -> None:
        self.user_repo = user_repo

    def get_user_by_uuid(self, uuid: UUID) -> User | None:
        db_user = self.user_repo.get_by_uuid(uuid)
        return db_user

    def get_all_users(
        self, offset: int, limit: int, sort_column: str, sort_order: str, search: str | None = None
    ) -> tuple[Sequence[User], int]:
        db_users, count = self.user_repo.get_users(offset, limit, sort_column, sort_order, search)

        return db_users, count

    def count_all_users(self) -> int:
        return self.user_repo.get_users_count()

    def get_user_by_auth_token(self, token: str) -> User | None:
        return self.user_repo.get_user_by_auth_token(token)
