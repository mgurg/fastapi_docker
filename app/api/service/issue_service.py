from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.api.repository.IssueRepo import IssueRepo
from app.api.repository.TagRepo import TagRepo


class IssueService:
    def __init__(
        self,
        issue_repo: Annotated[IssueRepo, Depends()],
        tag_repo: Annotated[TagRepo, Depends()],
    ) -> None:
        self.issue_repo = (issue_repo,)
        self.tag_repo = tag_repo

    def get_all(
        self,
        sort_column: str,
        sort_order: str,
        search: str | None,
        status: str | None,
        user: int | None,
        priority: str | None,
        date_from: datetime = None,
        date_to: datetime = None,
        tags: list[UUID] = None,
    ):
        if tags is not None:
            tag_ids = self.tag_repo.get_by_uuid(tag)  # FIX
