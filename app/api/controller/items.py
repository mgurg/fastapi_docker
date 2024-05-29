from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query

from app.api.service.item_service import ItemService
from app.models.models import User
from app.schemas.responses import ItemResponse, ItemsPaginated
from app.service.bearer_auth import check_token

item_test_router = APIRouter()

CurrentUser = Annotated[User, Depends(check_token)]
itemServiceDependency = Annotated[ItemService, Depends()]


# UserDB = Annotated[Session, Depends(get_session)]


@item_test_router.get("", response_model=ItemsPaginated)
def item_get_all(
    item_service: itemServiceDependency,
    search: Annotated[str | None, Query(max_length=50)] = None,
    limit: int = 10,
    offset: int = 0,
    field: Literal["name", "created_at"] = "name",
    order: Literal["asc", "desc"] = "asc",
):
    db_items, count = item_service.get_all_items(offset, limit, field, order, search)

    return ItemsPaginated(data=db_items, count=count, offset=offset, limit=limit)


@item_test_router.get("/{item_uuid}", response_model=ItemResponse)
def item_get_one(
    item_service: itemServiceDependency,
    item_uuid: UUID,
    auth_user: CurrentUser,
    tenant: Annotated[str | None, Header()] = None,
):
    db_item = item_service.get_item_by_uuid(item_uuid, tenant)

    return db_item
