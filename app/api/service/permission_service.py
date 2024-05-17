from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.api.repository.PermissionRepo import PermissionRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo


class PermissionService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends()],
        role_repo: Annotated[RoleRepo, Depends()],
        permission_repo: Annotated[PermissionRepo, Depends()],
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.permission_repo = permission_repo

    def get_all(self):
        return self.permission_repo.get_all_sorted()

    def get_role_by_uuid_with_permissions_and_users(self, role_uuid: UUID):
        return self.role_repo.get_by_uuid(role_uuid)
