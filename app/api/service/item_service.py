import csv
import io
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import Depends, HTTPException
from loguru import logger
from starlette.responses import StreamingResponse
from starlette.status import HTTP_404_NOT_FOUND

from app.api.repository.FileRepo import FileRepo
from app.api.repository.ItemRepo import ItemRepo
from app.api.repository.QrCodeRepo import QrCodeRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo
from app.models.models import Item
from app.schemas.requests import FavouritesAddIn, ItemAddIn, ItemEditIn
from app.storage.storage_interface import StorageInterface
from app.storage.storage_service_provider import get_storage_provider


class ItemService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends()],
        role_repo: Annotated[RoleRepo, Depends()],
        item_repo: Annotated[ItemRepo, Depends()],
        file_repo: Annotated[FileRepo, Depends()],
        qr_code_repo: Annotated[QrCodeRepo, Depends()],
        storage_provider: Annotated[StorageInterface, Depends(get_storage_provider)],
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.item_repo = item_repo
        self.file_repo = file_repo
        self.qr_code_repo = qr_code_repo
        self.storage_provider = storage_provider

    def get_item_by_uuid(self, item_uuid: UUID, tenant: str) -> Item | None:
        db_item = self.item_repo.get_by_uuid(item_uuid)

        if not db_item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found!")

        try:
            for picture in db_item.files_item:
                picture.url = self.storage_provider.get_url(f"{tenant}/{picture.uuid}_{picture.file_name}")
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

    def edit_item(self, item_uuid: UUID, item_data: ItemEditIn):
        db_item = self.item_repo.get_by_uuid(item_uuid)
        if not db_item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Item {item_uuid} not found!")

        item_data = item_data.model_dump(exclude_unset=True)

        if ("files" in item_data) and (item_data["files"] is not None):
            if len(item_data["files"]) > 0:
                db_item.files_item.clear()
                for file in item_data["files"]:
                    db_file = self.file_repo.get_by_uuid(file)
                    if db_file:
                        db_item.files_item.append(db_file)
            del item_data["files"]

        if ("text_html" in item_data) and (item_data["text_html"] is not None):
            item_data["text"] = BeautifulSoup(item_data["text_html"], "html.parser").get_text()
            del item_data["text_html"]

        item_data["updated_at"] = datetime.now(timezone.utc)

        self.item_repo.update(db_item.id, **item_data)

        return None


def add_item(self, item: ItemAddIn, tenant: str):
    # tenant_id = request.headers.get("tenant", None)
    # if not tenant_id:
    #     raise HTTPException(status_code=400, detail="Unknown Company!")
    #
    # company = get_public_company_from_tenant(tenant_id)
    #
    files = []
    if item.files is not None:
        for file in item.files:
            db_file = self.file_repo.get_by_uuid(file)
            if db_file:
                files.append(db_file)

    item_uuid = str(uuid4())

    qr_code_id = 1  # TODO: crud_qr.generate_item_qr_id(db)
    qr_code_company = "A"  # TODO:  crud_qr.add_noise_to_qr(company.qr_id)

    qr_code_data = {
        "uuid": str(uuid4()),
        "resource": "items",
        "resource_uuid": item_uuid,
        "qr_code_id": qr_code_id,
        "qr_code_full_id": f"{qr_code_company}+{qr_code_id}",
        "ecc": "L",
        "created_at": datetime.now(timezone.utc),
    }

    new_qr_code = self.qr_code_repo.create(**qr_code_data)
    #
    description = BeautifulSoup(item.text_html, "html.parser").get_text()

    item_data = {
        "uuid": item_uuid,
        "author_id": 1,  # TODO: auth_user.id,
        "name": item.name,
        "symbol": item.symbol,
        "summary": item.summary,
        "text": description,
        "text_json": item.text_json,
        "qr_code_id": new_qr_code.id,
        "files_item": files,
        "created_at": datetime.now(timezone.utc),
    }

    new_item = self.item_repo.create(**item_data)

    return new_item


def export(self) -> StreamingResponse:
    db_items, count = self.item_repo.get_items(0, 50, "name", "asc", None)
    f = io.StringIO()
    csv_file = csv.writer(f, delimiter=";")
    csv_file.writerow(["Name", "Description", "Symbol"])
    for item in db_items:
        csv_file.writerow([item.name, item.text, item.symbol])

    f.seek(0)
    response = StreamingResponse(f, media_type="text/csv")
    filename = f"items_{datetime.today().strftime('%Y-%m-%d')}.csv"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def delete_item(self, item_uuid: UUID, force: bool = False) -> bool:
    db_qr = self.qr_code_repo.get_by_resource_uuid(item_uuid)
    db_item = self.item_repo.get_by_uuid(item_uuid)

    if not db_item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Item {item_uuid} not found!")

    if force is False:
        self.item_repo.update(db_item.id, **{"deleted_at": datetime.now(timezone.utc)})
        return True

    for file in db_item.files_item:
        db_file = self.file_repo.get_by_uuid(file.uuid)

    # TODO: Guides / Guides_Files - add when refactored
    # for guide in db_item.item_guides:
    #     crud_guides.get_guide_by_uuid(db, guide.uuid)

    self.item_repo.delete(db_item.id)
    self.qr_code_repo.delete(db_qr.id)

    return True


def add_favourite(self, favourites: FavouritesAddIn) -> bool:
    db_item = self.item_repo.get_by_uuid(favourites.uuid)

    if not db_item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Item {favourites.uuid} not found!")

    for user in db_item.users_item:
        if user.uuid == favourites.user_uuid:
            db_item.users_item.remove(user)
            # TODO - check
            # db_item.users_item.remove(user)
            # db.add(user)
            # db.commit()
            return True

    db_user = self.user_repo.get_by_uuid(favourites.user_uuid)
    if not db_user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"User {favourites.user_uuid} not found")

    item_data = {"users_item": [db_user]}
    self.item_repo.update(db_item.id, **item_data)

    return True
