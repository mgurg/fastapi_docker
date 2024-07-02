from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import Depends, HTTPException
from loguru import logger
from starlette.status import HTTP_404_NOT_FOUND

from app.api.repository.FileRepo import FileRepo
from app.api.repository.GuideRepo import GuideRepo
from app.api.repository.IssueRepo import IssueRepo
from app.api.repository.ItemRepo import ItemRepo
from app.api.repository.QrCodeRepo import QrCodeRepo
from app.api.repository.TagRepo import TagRepo
from app.api.repository.UserRepo import UserRepo
from app.schemas.requests import GuideAddIn, GuideEditIn
from app.storage.storage_interface import StorageInterface
from app.storage.storage_service_provider import get_storage_provider


class GuideService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends()],
        issue_repo: Annotated[IssueRepo, Depends()],
        item_repo: Annotated[ItemRepo, Depends()],
        guide_repo: Annotated[GuideRepo, Depends()],
        tag_repo: Annotated[TagRepo, Depends()],
        file_repo: Annotated[FileRepo, Depends()],
        qr_code_repo: Annotated[QrCodeRepo, Depends()],
        storage_provider: Annotated[StorageInterface, Depends(get_storage_provider)],
    ) -> None:
        self.user_repo = user_repo
        self.issue_repo = issue_repo
        self.item_repo = item_repo
        self.guide_repo = guide_repo
        self.tag_repo = tag_repo
        self.file_repo = file_repo
        self.qr_code_repo = qr_code_repo
        self.storage_provider = storage_provider

    def get_all(
        self,
        offset: int,
        limit: int,
        sort_column: str,
        sort_order: str,
        search: str | None,
        item_uuid: UUID | None,
    ):
        item_id = None
        if item_uuid is not None:
            db_item = self.item_repo.get_by_uuid(item_uuid)
            if db_item is None:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Item `{item_uuid}` not found")
            item_id = db_item.id

        db_guides, count = self.guide_repo.get_guides(offset, limit, sort_column, sort_order, search, item_id)
        return db_guides, count

    def get_guide_by_uuid(self, guide_uuid: UUID, tenant: str):
        db_guide = self.guide_repo.get_by_uuid(guide_uuid)

        if not db_guide:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Guide `{guide_uuid}` not found!")

        try:
            for picture in db_guide.files_guide:
                s3_folder_path = f"{tenant}/{picture.uuid}_{picture.file_name}"
                picture.url = self.storage_provider.get_url(s3_folder_path)
        except Exception as e:
            logger.error(e)

        return db_guide

    def add(self, guide: GuideAddIn, tenant: str):
        related_item = None
        db_item = None

        if guide.item_uuid is not None:
            db_item = self.item_repo.get_by_uuid(guide.item_uuid)
            if not db_item:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND, detail=f"Related Item `{guide.item_uuid}` not found!"
                )
            related_item = [db_item]

        files = []
        if guide.files is not None:
            for file in guide.files:
                db_file = self.file_repo.get_by_uuid(file)
                if db_file:
                    files.append(db_file)

        description = BeautifulSoup(guide.text_html, "html.parser").get_text()

        # company = get_public_company_from_tenant(tenant_id)

        guide_uuid = str(uuid4())

        qr_code_id = 1  # TODO: crud_qr.generate_item_qr_id(db)
        qr_code_company = "A"  # TODO:  crud_qr.add_noise_to_qr(company.qr_id)

        qr_code_data = {
            "uuid": str(uuid4()),
            "resource": "guides",
            "resource_uuid": guide_uuid,
            "qr_code_id": qr_code_id,
            "qr_code_full_id": f"{qr_code_company}+{qr_code_id}",
            "ecc": "L",
            "created_at": datetime.now(timezone.utc),
        }

        new_qr_code = self.qr_code_repo.create(**qr_code_data)

        guide_data = {
            "uuid": guide_uuid,
            "author_id": 1,  # TODO: auth_user.id,
            "name": guide.name,
            "text": description,
            "qr_code_id": new_qr_code.id,
            "text_json": guide.text_json,
            "files_guide": files,
            "created_at": datetime.now(timezone.utc),
        }

        if related_item is not None:
            guide_data["item"] = [db_item]

        new_guide = self.guide_repo.create(**guide_data)

        return new_guide

    def edit(self, guide_uuid: UUID, guide: GuideEditIn) -> None:
        db_guide = self.guide_repo.get_by_uuid(guide_uuid)
        if not db_guide:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Guide `{guide_uuid}` not found!")

        guide_data = guide.model_dump(exclude_unset=True)

        if ("files" in guide_data) and (guide_data["files"] is not None):
            if len(guide_data["files"]) > 0:
                db_guide.files_guide.clear()
                for file in guide_data["files"]:
                    db_file = self.file_repo.get_by_uuid(file)
                    if db_file:
                        db_guide.files_guide.append(db_file)

            del guide_data["files"]

        if ("text_html" in guide_data) and (guide_data["text_html"] is not None):
            guide_data["text"] = BeautifulSoup(guide.text_html, "html.parser").get_text()

        guide_data["updated_at"] = datetime.now(timezone.utc)

        self.guide_repo.update(db_guide.id, **guide_data)

        return None

    def delete(self, guide_uuid: UUID) -> None:
        db_guide = self.guide_repo.get_by_uuid(guide_uuid)
        if not db_guide:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Guide `{guide_uuid}` not found")

        self.guide_repo.delete(db_guide.id)

        return None
