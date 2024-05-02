from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Params

from app.api.service.user_service import UserService
from app.schemas.responses import UserIndexResponse, UsersPaginated

user_test_router = APIRouter()


# CurrentUser = Annotated[User, Depends(has_token)]
# UserDB = Annotated[Session, Depends(get_session)]


@user_test_router.get("", response_model=UsersPaginated)
def user_get_all(
    user_service: Annotated[UserService, Depends()],
    params: Annotated[Params, Depends()],
    # auth_user: CurrentUser,
    # search: Annotated[str | None, Query(max_length=50)] = None,
    limit: int = 10,
    offset: int = 0,
    search: str | None = None,
    field: str = "name",
    order: str = "asc",
):
    if field not in ["first_name", "last_name", "created_at"]:
        field = "last_name"

    db_users, count = user_service.get_users(offset, limit, field, order, search)

    return UsersPaginated(data=db_users, count=count, offset=offset, limit=limit)


@user_test_router.get("/{user_uuid}", response_model=UserIndexResponse)
def user_get_one(user_service: Annotated[UserService, Depends()], user_uuid: str):
    user = user_service.get_user_by_uuid(UUID(user_uuid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
