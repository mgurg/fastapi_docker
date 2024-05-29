from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from loguru import logger
from starlette.status import HTTP_404_NOT_FOUND

from app.api.repository.ItemRepo import ItemRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo
from app.models.models import Item
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

    def get_item_by_uuid(self, item_uuid: UUID, tenant: str) -> Item | None:
        db_item = self.item_repo.get_by_uuid(item_uuid)

        if not db_item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found!")

        try:
            for picture in db_item.files_item:
                picture.url = generate_presigned_url(tenant, "_".join([str(picture.uuid), picture.file_name]))
        except Exception as e:
            logger.error("Error getting item by uuid", exc_info=e)

        return db_item

    def get_all_items(
        self,
        offset: int,
        limit: int,
        sort_column: str,
        sort_order: str,
        search: str | None = None,
        user_id: int | None = None,
    ):
        db_items, count = self.item_repo.get_items(offset, limit, sort_column, sort_order, search, user_id)

        return db_items, count
