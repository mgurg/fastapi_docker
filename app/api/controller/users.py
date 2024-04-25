from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from app.api.service.user_service import UserService
from app.schemas.responses import UserIndexResponse

user_test_router = APIRouter()


# CurrentUser = Annotated[User, Depends(has_token)]
# UserDB = Annotated[Session, Depends(get_session)]


@user_test_router.get("", response_model=list[UserIndexResponse])
def user_get_all(
        user_service: Annotated[UserService, Depends()],
        params: Annotated[Params, Depends()],
        # auth_user: CurrentUser,
        # search: Annotated[str | None, Query(max_length=50)] = None,
        search: str | None = None,
        field: str = "name",
        order: str = "asc",
):
    if field not in ["first_name", "last_name", "created_at"]:
        field = "last_name"

    db_users = user_service.get_users(field, order, search)

    # result = db.execute(db_users_query)  # await db.execute(query)
    # db_users = result.scalars().all()

    return db_users


@user_test_router.get("/{user_uuid}", response_model=UserIndexResponse)
def user_get_one(user_service: Annotated[UserService, Depends()], user_uuid: str):
    user = user_service.get_user_by_uuid(UUID(user_uuid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
