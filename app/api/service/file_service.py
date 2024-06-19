from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.api.repository.FileRepo import FileRepo
from app.api.repository.IssueRepo import IssueRepo
from app.models.models import File


class FileService:
    def __init__(
            self,
            file_repo: Annotated[FileRepo, Depends()],
            issue_repo: Annotated[IssueRepo, Depends()],
    ) -> None:
        self.file_repo = file_repo
        self.issue_repo = issue_repo

    def get_total_size_from_db(self) -> int:
        return self.file_repo.get_total_size_in_bytes() or 0

    def get_all(self):
        # TODO: missing download URL
        return self.file_repo.get_all()

    def get_one(self, uuid: UUID) -> File:
        db_file = self.file_repo.get_by_uuid(uuid)
        if not db_file:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"File `{uuid}` not found")

        return db_file
