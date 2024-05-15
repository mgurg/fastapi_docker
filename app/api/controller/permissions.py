from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from app.api.service.permission_service import PermissionService
from app.api.service.user_service import UserService
from app.models.models import User
from app.schemas.requests import UserCreateIn
from app.schemas.responses import StandardResponse, UserIndexResponse, UsersPaginated, PermissionResponse
from app.service.bearer_auth import check_token

permission_test_router = APIRouter()
CurrentUser = Annotated[User, Depends(check_token)]


@permission_test_router.get("/all", response_model=list[PermissionResponse])
def permissions_get_all(permission_service: Annotated[PermissionService, Depends()], auth_user: CurrentUser):
    all = permission_service.get_all()
