from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.api.service.item_service import ItemService
from app.models.models import User
from app.schemas.requests import FavouritesAddIn, ItemAddIn, ItemEditIn
from app.schemas.responses import ItemIndexResponse, ItemResponse, ItemsPaginated, StandardResponse
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


@item_test_router.get("/export")
def get_export_items(item_service: itemServiceDependency, auth_user: CurrentUser):
    return item_service.export()


@item_test_router.get("/{item_uuid}", response_model=ItemResponse)
def item_get_one(
        item_service: itemServiceDependency,
        item_uuid: UUID,
        auth_user: CurrentUser,
        tenant: Annotated[str | None, Header()] = None,
):
    db_item = item_service.get_item_by_uuid(item_uuid, tenant)

    return db_item


@item_test_router.post("", response_model=StandardResponse, status_code=HTTP_201_CREATED)
def user_add(
        item_service: itemServiceDependency,
        item: ItemAddIn,
        auth_user: CurrentUser,
        tenant: Annotated[str | None, Header()] = None,
):
    item = item_service.add_item(item, tenant)
    return {"ok": True}


@item_test_router.patch("/{item_uuid}", response_model=ItemIndexResponse)
def item_edit(item_service: itemServiceDependency, item_uuid: UUID, item_data: ItemEditIn, auth_user: CurrentUser):
    db_item = item_service.edit_item(item_uuid, item_data)
    return db_item


@item_test_router.delete("/{item_uuid}", status_code=HTTP_204_NO_CONTENT)
def item_delete(item_service: itemServiceDependency, item_uuid: UUID, auth_user: CurrentUser, force: bool = False):
    item_service.delete_item(item_uuid, force)
    return None


@item_test_router.post("/favourites", response_model=StandardResponse)
def item_add_to_favourites(item_service: itemServiceDependency, favourites: FavouritesAddIn, auth_user: CurrentUser):
    item_service.add_favourite(favourites)

    return {"ok": True}
