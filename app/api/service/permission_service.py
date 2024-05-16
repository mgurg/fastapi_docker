from typing import Annotated

from fastapi import Depends

from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo


class PermissionService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends()],
        role_repo: Annotated[RoleRepo, Depends()],
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
