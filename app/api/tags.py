from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import crud_issues, crud_tags
from app.db import get_db
from app.models.models import User
from app.schemas.requests import TagCreateIn, TagEditIn
from app.schemas.responses import StandardResponse, TagResponse
from app.service.bearer_auth import has_token

tag_router = APIRouter()

CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[Session, Depends(get_db)]


# @tag_router.get("/", response_model=list[TagResponse])
# def tags_get_all(
#     *, db: UserDB, auth_user: CurrentUser, field: str = "name", order: str = "asc", is_hidden: bool | None = None
# ):
#     if field not in ["name"]:
#         field = "name"
#
#     tags = crud_tags.get_tags(db, field, order, is_hidden)
#     return tags


# @tag_router.post("/", response_model=TagResponse)
# def tags_add_one(*, db: UserDB, tag: TagCreateIn, auth_user: CurrentUser):
#     db_tag = crud_tags.get_tag_by_name(db, tag.name)
#
#     if db_tag:
#         raise HTTPException(status_code=400, detail="Tag name already exists")
#
#     tag_data = {
#         "uuid": str(uuid4()),
#         "name": tag.name,
#         "color": tag.color,
#         "icon": tag.icon,
#         "author_id": auth_user.id,
#         "created_at": datetime.now(timezone.utc),
#     }
#
#     tag = crud_tags.create_tag(db, tag_data)
#
#     return tag


# @tag_router.patch("/{tag_uuid}", response_model=TagResponse)
# def tags_edit_one(*, db: UserDB, tag_uuid: UUID, tag: TagEditIn, auth_user: CurrentUser):
#     db_tag = crud_tags.get_tag_by_uuid(db, tag_uuid)
#
#     tag_data = {"is_hidden": tag.is_hidden}
#     if tag.color is not None:
#         tag_data["color"] = tag.color.as_hex()
#
#     crud_tags.update_tag(db, db_tag, tag_data)
#     return db_tag


# @tag_router.delete("/{tag_uuid}", response_model=StandardResponse)
# def tags_delete_one(*, db: UserDB, tag_uuid: UUID, auth_user: CurrentUser, force_delete: bool = False):
#     db_tag = crud_tags.get_tag_by_uuid(db, tag_uuid)
#
#     if not db_tag:
#         raise HTTPException(status_code=404, detail="Tag not found")
#
#     tag_usage = crud_issues.count_issues_by_tag(db, db_tag.id)
#
#     if tag_usage > 0:
#         raise HTTPException(status_code=400, detail="Tag in use")
#
#     # print(tag_usage)
#     db.delete(db_tag)
#     db.commit()
#
#     return {"ok": True}
