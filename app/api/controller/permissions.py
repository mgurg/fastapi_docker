from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.service.permission_service import PermissionService
from app.models.models import User
from app.schemas.responses import PermissionResponse
from app.service.bearer_auth import check_token

permission_test_router = APIRouter()
CurrentUser = Annotated[User, Depends(check_token)]


@permission_test_router.get("/all", response_model=list[PermissionResponse])
def permissions_get_all(permission_service: Annotated[PermissionService, Depends()], auth_user: CurrentUser):
    all = permission_service.get_all()
