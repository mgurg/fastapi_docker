from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, Form, Header, File
from starlette.status import HTTP_204_NO_CONTENT

from app.api.service.file_service import FileService
from app.models.models import User
from app.schemas.responses import FileResponse
from app.service.bearer_auth import check_token

file_test_router = APIRouter()

MAX_UPLOAD_SIZE_MB: int = 5 * 1024 * 1024

fileServiceDependency = Annotated[FileService, Depends()]
CurrentUser = Annotated[User, Depends(check_token)]


def valid_content_length(
        content_length: Annotated[int, Header(le=MAX_UPLOAD_SIZE_MB)],
) -> int:
    return content_length


@file_test_router.get("/used_space", response_model=int)
def file_get_used_space(file_service: fileServiceDependency, auth_user: CurrentUser):
    db_file_size = file_service.get_total_size_from_db()

    return db_file_size


@file_test_router.get("/", response_model=list[FileResponse])
def file_get_info_all(file_service: fileServiceDependency, auth_user: CurrentUser):
    db_files = file_service.get_all()

    return db_files


@file_test_router.get("/{uuid}", response_model=FileResponse, name="file:GetInfoFromDB")
def file_get_info_single(file_service: fileServiceDependency, uuid: UUID, auth_user: CurrentUser):
    db_files = file_service.get_one(uuid)

    return db_files


@file_test_router.post("/", response_model=FileResponse)
def file_add(
        file_service: fileServiceDependency,
        auth_user: CurrentUser,
        file: Annotated[UploadFile, File()],
        file_size: Annotated[int, Depends(valid_content_length)],
        uuid: UUID | None = Form(None),
        tenant: Annotated[str | None, Header()] = None,
):
    uploaded_file = file_service.upload(file, file_size, tenant, auth_user.id, uuid)
    return uploaded_file


@file_test_router.delete("/{file_uuid}", status_code=HTTP_204_NO_CONTENT)
def remove_file(file_service: fileServiceDependency, file_uuid: UUID, auth_user: CurrentUser,
                tenant: Annotated[str | None, Header()] = None):
    file_service.delete_file(file_uuid, tenant)


@file_test_router.get("/presigned_url/{file}")
def file_download_pre_signed(file_service: fileServiceDependency, tenant: Annotated[str | None, Header()], file_name: str ):
    presigned_url = file_service.get_presigned_url(tenant, file_name)
    return presigned_url
