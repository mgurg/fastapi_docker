from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.service.permission_service import PermissionService
from app.models.models import User
from app.schemas.responses import PermissionResponse, RolePermissionFull
from app.service.bearer_auth import check_token

permission_test_router = APIRouter()
CurrentUser = Annotated[User, Depends(check_token)]


@permission_test_router.get("/all", response_model=list[PermissionResponse])
def permissions_get_all(permission_service: Annotated[PermissionService, Depends()], auth_user: CurrentUser):
    return permission_service.get_all()


@permission_test_router.get("/{role_uuid}", response_model=RolePermissionFull)
def role_get_one(permission_service: Annotated[PermissionService, Depends()], auth_user: CurrentUser, role_uuid: UUID):
    return permission_service.get_role_by_uuid_with_permissions_and_users(role_uuid)
