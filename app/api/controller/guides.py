from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from starlette.status import HTTP_204_NO_CONTENT

from app.api.service.guide_service import GuideService
from app.models.models import User
from app.schemas.requests import GuideAddIn, GuideEditIn
from app.schemas.responses import GuideIndexResponse, GuideResponse, GuidesPaginated
from app.service.bearer_auth import check_token

guide_test_router = APIRouter()

CurrentUser = Annotated[User, Depends(check_token)]
guideServiceDependency = Annotated[GuideService, Depends()]


@guide_test_router.get("", response_model=GuidesPaginated)
def guide_get_all(
    guide_service: guideServiceDependency,
    auth_user: CurrentUser,
    search: str = None,
    item_uuid: UUID | None = None,
    limit: int = 10,
    offset: int = 0,
    field: Literal["created_at", "name", "priority", "status"] = "name",
    order: Literal["asc", "desc"] = "asc",
):
    db_guides, count = guide_service.get_all(offset, limit, field, order, search, item_uuid)
    return GuidesPaginated(data=db_guides, count=count, offset=offset, limit=limit)


@guide_test_router.get("/{guide_uuid}", response_model=GuideIndexResponse)  # , response_model=Page[UserIndexResponse]
def guide_get_one(
    guide_service: guideServiceDependency,
    guide_uuid: UUID,
    tenant: Annotated[str | None, Header()],
    auth_user: CurrentUser,
):
    return guide_service.get_guide_by_uuid(guide_uuid, tenant)


@guide_test_router.post("/", response_model=GuideResponse)
def guide_add(
    guide_service: guideServiceDependency,
    tenant: Annotated[str | None, Header()],
    guide: GuideAddIn,
    auth_user: CurrentUser,
):
    guide_service.add(guide, tenant)


@guide_test_router.patch("/{guide_uuid}", response_model=GuideResponse)
def guide_edit(guide_service: guideServiceDependency, guide_uuid: UUID, guide: GuideEditIn, auth_user: CurrentUser):
    guide_service.edit(guide_uuid, guide)


@guide_test_router.delete("/{guide_uuid}", status_code=HTTP_204_NO_CONTENT)
def guide_delete(guide_service: guideServiceDependency, guide_uuid: UUID, auth_user: CurrentUser):
    guide_service.delete(guide_uuid)

    return None
