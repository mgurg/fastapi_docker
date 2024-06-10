from datetime import datetime, timezone
from typing import Annotated
from uuid import uuid4, UUID

from fastapi import Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.api.repository.IssueRepo import IssueRepo
from app.api.repository.TagRepo import TagRepo
from app.models.models import Tag
from app.schemas.requests import TagCreateIn, TagEditIn


class TagService:
    def __init__(
            self,
            tag_repo: Annotated[TagRepo, Depends()],
            issue_repo: Annotated[IssueRepo, Depends()],
    ) -> None:
        self.tag_repo = tag_repo
        self.issue_repo = issue_repo

    def get_all(self,
                offset: int,
                limit: int,
                sort_column: str,
                sort_order: str,
                is_hidden: bool | None = None):
        db_tags, count = self.tag_repo.get_tags(offset, limit, sort_column, sort_order, is_hidden)

        return db_tags, count

    def add(self, tag: TagCreateIn, user_id: int) -> Tag:
        db_tag = self.tag_repo.get_by_name(tag.name)
        if db_tag:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Tag `{tag.name}` already exists")

        tag_data = {
            "uuid": str(uuid4()),
            "name": tag.name,
            "color": tag.color,
            "icon": tag.icon,
            "author_id": user_id,
            "created_at": datetime.now(timezone.utc),
        }
        new_tag = self.tag_repo.create(**tag_data)
        return new_tag

    def update(self, tag_uuid: UUID, tag: TagEditIn) -> None:

        db_tag = self.tag_repo.get_by_uuid(tag_uuid)

        tag_data = {"is_hidden": tag.is_hidden}
        if tag.color is not None:
            tag_data["color"] = tag.color.as_hex()

        # TODO: dodać możliwosć zmiany nazwy?

        self.tag_repo.update(db_tag.id, **tag_data)

    def delete_tag(self, tag_uuid: UUID) -> None:

        db_tag = self.tag_repo.get_by_uuid(tag_uuid)
        if not db_tag:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Tag `{tag_uuid}` not found")

        tag_usage = self.issue_repo.count_by_tag(db_tag.id)

        if tag_usage > 0:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Tag `{db_tag.name}` already in use")

        self.tag_repo.delete(db_tag.id)
