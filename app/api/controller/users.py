from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.api.service.user_service import UserService
from app.models.models import User
from app.schemas.requests import UserCreateIn
from app.schemas.responses import StandardResponse, UserIndexResponse, UsersPaginated
from app.service.bearer_auth import check_token

user_test_router = APIRouter()

CurrentUser = Annotated[User, Depends(check_token)]


# UserDB = Annotated[Session, Depends(get_session)]


@user_test_router.get("", response_model=UsersPaginated)
def get_all_users(
    user_service: Annotated[UserService, Depends()],
    # auth_user: CurrentUser,
    search: Annotated[str | None, Query(max_length=50)] = None,
    limit: int = 10,
    offset: int = 0,
    field: str = "name",
    order: str = "asc",
):
    if field not in ["first_name", "last_name", "created_at"]:
        field = "last_name"

    db_users, count = user_service.get_all_users(offset, limit, field, order, search)
    return UsersPaginated(data=db_users, count=count, offset=offset, limit=limit)


@user_test_router.get("/count")
def get_users_count(user_service: Annotated[UserService, Depends()], auth_user: CurrentUser):
    db_user_cnt = user_service.count_all_users()

    return db_user_cnt


@user_test_router.get("/{user_uuid}", response_model=UserIndexResponse)
def get_one_user(user_service: Annotated[UserService, Depends()], user_uuid: str):
    user = user_service.get_user_by_uuid(UUID(user_uuid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_test_router.post("", response_model=StandardResponse, status_code=HTTP_201_CREATED)
def user_add(
    user_service: Annotated[UserService, Depends()], user: UserCreateIn, request: Request, auth_user: CurrentUser
):
    user = user_service.add_user(user, request.headers.get("tenant", None))
    return {"ok": True}


@user_test_router.patch("/{user_uuid}", response_model=StandardResponse)
def user_edit(
    user_service: Annotated[UserService, Depends()], user_uuid: UUID, user: UserCreateIn, auth_user: CurrentUser
):
    user = user_service.edit_user(user_uuid, user)
    return {"ok": True}


@user_test_router.delete("/{user_uuid}", status_code=HTTP_204_NO_CONTENT)
def delete_user(user_service: Annotated[UserService, Depends()], user_uuid: str, force: bool = False):
    user = user_service.delete_user(UUID(user_uuid), force)
