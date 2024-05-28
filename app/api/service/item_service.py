import codecs
import csv
import io
import sys
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy import Sequence
from starlette.responses import StreamingResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.api.repository.ItemRepo import ItemRepo
from app.api.repository.PublicUserRepo import PublicUserRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo
from app.models.models import User, Item
from app.schemas.requests import UserCreateIn
from app.service.password import Password
from app.storage.aws_s3 import generate_presigned_url


class ItemService:
    def __init__(
            self,
            user_repo: Annotated[UserRepo, Depends()],
            role_repo: Annotated[RoleRepo, Depends()],
            item_repo: Annotated[ItemRepo, Depends()],
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.item_repo = item_repo

    def get_item_by_uuid(self, item_uuid: UUID) -> Item | None:
        db_item = self.item_repo.get_by_uuid(item_uuid)

        if not db_item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found!")

        try:
            for picture in db_item.files_item:
                picture.url = generate_presigned_url(
                    # TODO: Annotaed
                    request.headers.get("tenant", "public"), "_".join([str(picture.uuid), picture.file_name])
                )
        except Exception as e:
            capture_exception(e)
