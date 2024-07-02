from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.status import HTTP_204_NO_CONTENT

from app.api.service.permission_service import PermissionService
from app.models.models import User
from app.schemas.requests import RoleAddIn, RoleEditIn
from app.schemas.responses import PermissionResponse, RolePermissionFull, RolesPaginated
from app.service.bearer_auth import check_token

permission_test_router = APIRouter()
permissionServiceDependency = Annotated[PermissionService, Depends()]
CurrentUser = Annotated[User, Depends(check_token)]


@permission_test_router.get("", response_model=RolesPaginated)
def role_get_all(
        permission_service: permissionServiceDependency,
        auth_user: CurrentUser,
        search: str = None,
        all: bool = True,
        limit: int = 10,
        offset: int = 0,
        field: Literal["created_at", "name", "priority", "status"] = "name",
        order: Literal["asc", "desc"] = "asc",
):
    db_roles, count = permission_service.get_all_roles(offset, limit, "role_title", order, search, all)

    return RolesPaginated(data=db_roles, count=count, offset=offset, limit=limit)


@permission_test_router.get("/all", response_model=list[PermissionResponse])  # response_model=list[PermissionResponse]
def permissions_get_all(permission_service: Annotated[PermissionService, Depends()], auth_user: CurrentUser):
    return permission_service.get_all()


@permission_test_router.get("/{role_uuid}", response_model=RolePermissionFull)
def role_get_one(permission_service: Annotated[PermissionService, Depends()], auth_user: CurrentUser, role_uuid: UUID):
    return permission_service.get_role_by_uuid_with_permissions_and_users(role_uuid)


@permission_test_router.post("", response_model=RolePermissionFull)
def role_add(permission_service: Annotated[PermissionService, Depends()], role: RoleAddIn, auth_user: CurrentUser):
    return permission_service.add_role(role)


@permission_test_router.patch("/{role_uuid}", status_code=HTTP_204_NO_CONTENT)
def role_edit(permission_service: Annotated[PermissionService, Depends()], role_uuid: UUID, role: RoleEditIn,
              auth_user: CurrentUser):
    permission_service.edit_role(role_uuid, role)
    return None


@permission_test_router.delete("/{role_uuid}", status_code=HTTP_204_NO_CONTENT)
def role_delete(permission_service: Annotated[PermissionService, Depends()], role_uuid: UUID, auth_user: CurrentUser):
    permission_service.delete_role(role_uuid)
    return None
