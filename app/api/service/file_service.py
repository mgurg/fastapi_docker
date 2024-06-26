from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, UploadFile
from loguru import logger
from starlette.responses import StreamingResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_413_REQUEST_ENTITY_TOO_LARGE

from app.api.repository.FileRepo import FileRepo
from app.api.repository.IssueRepo import IssueRepo
from app.config import get_settings
from app.models.models import File
from app.storage.storage_interface import StorageInterface
from app.storage.storage_service_provider import get_storage_provider
from app.utils.filename_utils import get_safe_filename

settings = get_settings()


class FileService:
    def __init__(
        self,
        file_repo: Annotated[FileRepo, Depends()],
        issue_repo: Annotated[IssueRepo, Depends()],
        storage_provider: Annotated[StorageInterface, Depends(get_storage_provider)],
    ) -> None:
        self.file_repo = file_repo
        self.issue_repo = issue_repo
        self.storage_provider = storage_provider

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

    def download(self, file_uuid: UUID, tenant: str):
        db_file = self.file_repo.get_by_uuid(file_uuid)
        if not db_file:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"File `{file_uuid}` not found")

        try:
            s3_folder_path = f"{tenant}/{file_uuid}_{db_file.file_name}"
            file = self.storage_provider.download_file(s3_folder_path)
            header = {"Content-Disposition": f'inline; filename="{db_file.file_name}"'}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=404, detail="File not found")

        return StreamingResponse(file, media_type=db_file.mimetype, headers=header)

    async def upload(
        self, file: UploadFile, file_size: int, tenant: str, user_id: int, uuid: UUID | None = None
    ) -> File:
        used_quota = self.get_total_size_from_db()

        if used_quota > 50 * 1024 * 1024:
            raise HTTPException(status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Quota exceeded")

        file_uuid = str(uuid4()) if not uuid else str(uuid)
        safe_filename = get_safe_filename(file.filename)
        s3_folder_path = f"{tenant}/{file_uuid}_{safe_filename}"

        # Reset the file cursor to the beginning
        await file.seek(0)

        success = self.storage_provider.upload_file(file.file, s3_folder_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to upload file to storage")

        file_data = {
            "uuid": file_uuid,
            "owner_id": user_id,
            "file_name": safe_filename,
            "extension": Path(safe_filename).suffix,
            "mimetype": file.content_type,
            "size": file_size,
            "created_at": datetime.now(timezone.utc),
        }

        new_file = self.file_repo.create(**file_data)
        s3_folder_path = f"{tenant}/{file_uuid}_{safe_filename}"
        new_file.url = self.storage_provider.get_url(s3_folder_path)

        return new_file


def delete_file(self, file_uuid: UUID, tenant: str) -> None:
    db_file = self.file_repo.get_by_uuid(file_uuid)
    if not db_file:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"File `{file_uuid}` not found")

    s3_folder_path = f"{tenant}/{file_uuid}_{db_file.file_name}"

    success = self.storage_provider.delete_file(s3_folder_path)
    if not success:
        logger.exception("Failed to delete S3 object")
        raise HTTPException(status_code=500, detail=f"Failed to delete file `{file_uuid}` from storage")

    self.file_repo.delete(db_file.id)

    return None


def get_presigned_url(self, file_uuid: UUID, tenant: str) -> str:
    db_file = self.file_repo.get_by_uuid(file_uuid)
    if not db_file:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"File `{file_uuid}` not found")

    s3_folder_path = f"{tenant}/{file_uuid}_{db_file.file_name}"
    return self.storage_provider.get_url(s3_folder_path)
