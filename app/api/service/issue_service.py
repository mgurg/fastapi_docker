import csv
import io
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from loguru import logger
from starlette.responses import StreamingResponse
from starlette.status import HTTP_404_NOT_FOUND

from app.api.repository.IssueRepo import IssueRepo
from app.api.repository.TagRepo import TagRepo
from app.api.repository.UserRepo import UserRepo
from app.storage.storage_interface import StorageInterface
from app.storage.storage_service_provider import get_storage_provider


class IssueService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends()],
        issue_repo: Annotated[IssueRepo, Depends()],
        tag_repo: Annotated[TagRepo, Depends()],
        storage_provider: Annotated[StorageInterface, Depends(get_storage_provider)],
    ) -> None:
        self.user_repo = user_repo
        self.issue_repo = issue_repo
        self.tag_repo = tag_repo
        self.storage_provider = storage_provider

    def get_all(
        self,
        offset: int,
        limit: int,
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

        db_issues, count = self.issue_repo.get_issues(
            offset, limit, sort_column, sort_order, search, status, user_id, priority, date_from, date_to, tag_ids
        )
        return db_issues, count

    def export(self):
        db_issues, count = self.issue_repo.get_issues(0, 50, "name", "asc", None, "all", None, None, None, None, None)

        f = io.StringIO()
        csv_file = csv.writer(f, delimiter=";")
        csv_file.writerow(["Symbol", "Name", "Description", "Author", "Status", "Created at"])
        for u in db_issues:
            csv_file.writerow([u.symbol, u.name, u.text, u.author_name, u.status, u.created_at])

        f.seek(0)
        response = StreamingResponse(f, media_type="text/csv")
        filename = f"issues_{datetime.today().strftime('%Y-%m-%d')}.csv"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    def get_issue_by_uuid(self, issue_uuid: UUID, tenant: str):
        db_issue = self.issue_repo.get_by_uuid(issue_uuid)
        if not db_issue:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Issue `{issue_uuid}` not found!")

        try:
            for picture in db_issue.files_issue:
                s3_folder_path = f"{tenant}/{picture.uuid}_{picture.file_name}"
                picture.url = self.storage_provider.get_url(s3_folder_path)
        except Exception as e:
            logger.error(e)

        return db_issue
