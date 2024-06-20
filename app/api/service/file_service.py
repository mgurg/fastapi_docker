from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, UploadFile
from starlette.status import HTTP_404_NOT_FOUND, HTTP_413_REQUEST_ENTITY_TOO_LARGE

from app.api.repository.FileRepo import FileRepo
from app.api.repository.IssueRepo import IssueRepo
from app.config import get_settings
from app.models.models import File
from app.storage.aws_s3 import s3_resource, generate_presigned_url

settings = get_settings()


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

    def upload(self, file: UploadFile, file_size: int, tenant: str, user_id: int, uuid: UUID | None = None) -> File:

        used_quota = self.get_total_size_from_db()

        if used_quota > 50000000:  # ~5MB
            used_quota_mb = used_quota / (1024 * 1024)
            raise HTTPException(status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                detail=f"Quota exceeded. Used: {used_quota_mb:.2f} MB")

        file_uuid = str(uuid4()) if not uuid else uuid

        try:
            s3_folder_path = "".join([tenant, "/", file_uuid, "_", file.filename])

            s3_resource.Bucket(settings.s3_bucket_name).upload_fileobj(Fileobj=file.file, Key=s3_folder_path)
        except Exception as e:
            print(e)

        file_data = {
            "uuid": file_uuid,
            "owner_id": user_id,
            "file_name": file.filename,
            "file_description": None,
            "extension": Path(file.filename).suffix,
            "mimetype": file.content_type,
            "size": file_size,
            "created_at": datetime.now(timezone.utc),
        }

        new_file = self.file_repo.create(**file_data)

        new_file.url = generate_presigned_url(
            tenant, "_".join([str(file_uuid), file.filename])
        )

        return new_file
