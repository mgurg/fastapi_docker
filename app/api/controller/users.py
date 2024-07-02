from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from app.api.service.user_service import UserService
from app.models.models import User
from app.schemas.requests import UserCreateIn
from app.schemas.responses import StandardResponse, UserIndexResponse, UsersPaginated
from app.service.acl import ACL
from app.service.bearer_auth import check_token

user_test_router = APIRouter()

CurrentUser = Annotated[User, Depends(check_token)]
userServiceDependency = Annotated[UserService, Depends()]


@user_test_router.get("", response_model=UsersPaginated)
def get_all_users(
    user_service: userServiceDependency,
    # auth_user: CurrentUser,
    search: Annotated[str | None, Query(max_length=50)] = None,
    limit: int = 10,
    offset: int = 0,
    field: Literal["first_name", "last_name", "created_at"] = "name",
    order: Literal["asc", "desc"] = "asc",
):
    db_users, count = user_service.get_all_users(offset, limit, field, order, search)
    return UsersPaginated(data=db_users, count=count, offset=offset, limit=limit)


@user_test_router.get("/count")
def get_users_count(user_service: userServiceDependency, auth_user: CurrentUser):
    ACL(auth_user).no_required()
    db_user_cnt = user_service.count_all_users()
    return db_user_cnt


@user_test_router.get("/export")
def get_export_users(user_service: userServiceDependency, auth_user: CurrentUser):
    return user_service.export()


@user_test_router.post("/import")
def get_import_users(user_service: userServiceDependency, auth_user: CurrentUser, file: UploadFile | None = None):
    if not file:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="No file sent")
    return user_service.import_users(file)


@user_test_router.get("/{user_uuid}", response_model=UserIndexResponse)
def get_one_user(user_service: userServiceDependency, user_uuid: UUID):
    user = user_service.get_user_by_uuid(user_uuid)

    return user


@user_test_router.post("", response_model=StandardResponse, status_code=HTTP_201_CREATED)
def user_add(user_service: userServiceDependency, user: UserCreateIn, request: Request, auth_user: CurrentUser):
    user_service.add_user(user, request.headers.get("tenant", None))
    return None


@user_test_router.patch("/{user_uuid}", status_code=HTTP_204_NO_CONTENT)
def user_edit(user_service: userServiceDependency, user_uuid: UUID, user: UserCreateIn, auth_user: CurrentUser):
    user_service.edit_user(user_uuid, user)
    return None


@user_test_router.delete("/{user_uuid}", status_code=HTTP_204_NO_CONTENT)
def delete_user(user_service: userServiceDependency, user_uuid: UUID, force: bool = False):
    user_service.delete_user(user_uuid, force)
    return None
