from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.service.file_service import FileService
from app.models.models import User
from app.schemas.responses import FileResponse
from app.service.bearer_auth import check_token

file_test_router = APIRouter()

fileServiceDependency = Annotated[FileService, Depends()]
CurrentUser = Annotated[User, Depends(check_token)]


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