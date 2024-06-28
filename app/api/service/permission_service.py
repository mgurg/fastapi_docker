from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.api.repository.PermissionRepo import PermissionRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo
from app.schemas.requests import RoleAddIn, RoleEditIn
from app.service.helpers import to_snake_case


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

    def get_all_roles(
            self,
            offset: int,
            limit: int,
            sort_column: str,
            sort_order: str,
            search: str | None,
            all: bool
    ):
        db_roles, count = self.role_repo.get_roles_summary(offset, limit, sort_column, sort_order, search, all)
        return db_roles, count

    def get_all(self):
        return self.permission_repo.get_all_sorted()

    def get_role_by_uuid_with_permissions_and_users(self, role_uuid: UUID):
        return self.role_repo.get_by_uuid(role_uuid)

    def add_role(self, role: RoleAddIn):
        db_role = self.permission_repo.get_role_by_name(role.title)
        if db_role:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Role `{role.title}` already exists!")

        permissions = []
        if role.permissions is not None:
            for permissions_uuid in role.permissions:
                db_permission = self.permission_repo.get_by_uuid(permissions_uuid)
                if db_permission:
                    permissions.append(db_permission)

        role_data = {
            "uuid": str(uuid4()),
            "is_custom": True,
            "is_visible": True,
            "is_system": False,
            "role_name": role.title,
            "role_title": role.title,
            "role_description": role.description,
            "permission": permissions,
        }

        new_role = self.role_repo.create(**role_data)
        return new_role

    def edit_role(self, role_uuid: UUID, role: RoleEditIn):
        db_role = self.role_repo.get_by_uuid(role_uuid)
        if not db_role:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Role already exists!")

        role_data = role.model_dump(exclude_unset=True)

        if ("permissions" in role_data) and (role_data["permissions"] is not None):
            if len(role_data["permissions"]) > 0:
                db_role.permission.clear()
                for permission in role_data["permissions"]:
                    db_permission = self.permission_repo.get_by_uuid(permission)
                    if db_permission:
                        db_role.permission.append(db_permission)
            del role_data["permissions"]

        # TODO: simplify names
        role_data["role_name"] = to_snake_case(role.title)
        role_data["role_title"] = role.title
        role_data["role_description"] = role.description

        del role_data["title"]
        del role_data["description"]

        self.role_repo.update(db_role.id, **role_data)

        return None

    def delete_role(self, role_uuid: UUID):
        db_role = self.role_repo.get_by_uuid(role_uuid)

        if not db_role:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Role `{role_uuid}` not found")

        db_users = self.user_repo.get_users_by_role_id(db_role.id)

        if db_users:
            error_message = {"message": "Permission assigned to one or more users", "count": len(db_users)}
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=error_message)

        self.role_repo.delete(db_role.id)

        return None
