from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.status import HTTP_204_NO_CONTENT

from app.api.service.tag_service import TagService
from app.models.models import User
from app.schemas.requests import TagCreateIn, TagEditIn
from app.schemas.responses import TagResponse, TagsPaginated
from app.service.bearer_auth import check_token

tag_test_router = APIRouter()

CurrentUser = Annotated[User, Depends(check_token)]
tagServiceDependency = Annotated[TagService, Depends()]


# UserDB = Annotated[Session, Depends(get_session)]


@tag_test_router.get("", response_model=TagsPaginated)
def issues_get_all(
    tag_service: tagServiceDependency,
    is_hidden: bool | None = None,
    limit: int = 10,
    offset: int = 0,
    field: Literal["name"] = "name",
    order: Literal["asc", "desc"] = "asc",
):
    db_tags, count = tag_service.get_all(offset, limit, field, order, is_hidden)

    return TagsPaginated(data=db_tags, count=count, offset=offset, limit=limit)


@tag_test_router.post("", response_model=TagResponse)
def tags_add_one(tag_service: tagServiceDependency, tag: TagCreateIn, auth_user: CurrentUser):
    db_tag = tag_service.add(tag, auth_user.id)
    return db_tag


@tag_test_router.patch("/{tag_uuid}", status_code=HTTP_204_NO_CONTENT)
def tags_edit_one(tag_service: tagServiceDependency, tag_uuid: UUID, tag: TagEditIn, auth_user: CurrentUser):
    tag_service.update(tag_uuid, tag)
    return None


@tag_test_router.delete("/{tag_uuid}", status_code=HTTP_204_NO_CONTENT)
def tags_delete_one(tag_service: tagServiceDependency, tag_uuid: UUID, auth_user: CurrentUser):
    tag_service.delete_tag(tag_uuid)
    return None
