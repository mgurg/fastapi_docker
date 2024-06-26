from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.api.repository.IssueRepo import IssueRepo
from app.api.repository.TagRepo import TagRepo
from app.api.repository.UserRepo import UserRepo


class IssueService:
    def __init__(
            self,
            user_repo: Annotated[UserRepo, Depends()],
            issue_repo: Annotated[IssueRepo, Depends()],
            tag_repo: Annotated[TagRepo, Depends()],
    ) -> None:
        self.user_repo = user_repo
        self.issue_repo = issue_repo
        self.tag_repo = tag_repo

    def get_all(
            self,
            sort_column: str,
            sort_order: str,
            search: str | None,
            status: str | None,
            user_uuid: UUID | None,
            priority: str | None,
            date_from: datetime = None,
            date_to: datetime = None,
            tags: list[UUID] = None,
    ):
        tag_ids = self.tag_repo.get_ids_by_tags_uuid(tags) if tags else None

        user_id = None
        if user_uuid is not None:
            db_user = self.user_repo.get_by_uuid(user_uuid)
            if db_user is None:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"User `{user_uuid}` not found")
            user_id = db_user.id


