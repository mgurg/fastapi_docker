from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.api.service.item_service import ItemService
from app.api.service.user_service import UserService
from app.models.models import User
from app.schemas.requests import UserCreateIn
from app.schemas.responses import StandardResponse, UserIndexResponse, UsersPaginated, ItemResponse
from app.service.acl import ACL
from app.service.bearer_auth import check_token

item_test_router = APIRouter()

CurrentUser = Annotated[User, Depends(check_token)]
itemServiceDependency = Annotated[ItemService, Depends()]


# UserDB = Annotated[Session, Depends(get_session)]


@item_test_router.get("/{item_uuid}", response_model=ItemResponse)
def item_get_one(item_service: itemServiceDependency, item_uuid: UUID, request: Request, auth_user: CurrentUser):
    db_item = item_service.get_item_by_uuid(item_uuid)

    return db_item
