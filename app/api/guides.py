from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session

from app.crud import crud_files, crud_guides, crud_items, crud_qr
from app.crud.crud_auth import get_public_company_from_tenant
from app.db import get_db
from app.models.models import User
from app.schemas.requests import GuideAddIn, GuideEditIn
from app.schemas.responses import GuideIndexResponse, GuideResponse, StandardResponse
from app.service.bearer_auth import has_token

# from app.schemas.schemas import GuideIndexResponse
from app.storage.aws_s3 import generate_presigned_url

guide_router = APIRouter()

CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[Session, Depends(get_db)]


@guide_router.get("/", response_model=Page[GuideResponse])  #
def guide_get_all(
    *,
    db: UserDB,
    params: Annotated[Params, Depends()],
    auth_user: CurrentUser,
    search: str = None,
    item_uuid: UUID | None = None,
    order: str = "asc",
    field: str = "name",
):
    if field not in ["name"]:
        field = "name"

    item_id = None
    if item_uuid is not None:
        db_item = crud_items.get_item_by_uuid(db, item_uuid)
        if db_item is None:
            raise HTTPException(status_code=401, detail="Item not found")
        item_id = db_item.id

    db_guides_query = crud_guides.get_guides(search, item_id, field, order)

    # result = db.execute(db_guides_query)  # await db.execute(query)
    # db_guides = result.scalars().all()

    return paginate(db, db_guides_query)


@guide_router.get("/{guide_uuid}", response_model=GuideIndexResponse)  # , response_model=Page[UserIndexResponse]
def guide_get_one(*, db: UserDB, guide_uuid: UUID, request: Request, auth_user: CurrentUser):
    db_guide = crud_guides.get_guide_by_uuid(db, guide_uuid)

    if not db_guide:
        raise HTTPException(status_code=400, detail="Guide not found!")

    try:
        for picture in db_guide.files_guide:
            picture.url = generate_presigned_url(
                request.headers.get("tenant", "public"), "_".join([str(picture.uuid), picture.file_name])
            )
    except Exception as e:
        capture_exception(e)

    return db_guide


@guide_router.post("/", response_model=GuideResponse)
def guide_add(*, db: UserDB, request: Request, guide: GuideAddIn, auth_user: CurrentUser):
    tenant_id = request.headers.get("tenant", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Unknown Company!")

    related_item = None
    db_item = None

    if guide.item_uuid is not None:
        db_item = crud_items.get_item_by_uuid(db, guide.item_uuid)
        if not db_item:
            raise HTTPException(status_code=400, detail="Related Item not found!")
        related_item = [db_item]

    files = []
    if guide.files is not None:
        for file in guide.files:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

    description = BeautifulSoup(guide.text_html, "html.parser").get_text()

    # company = None
    # schema_translate_map = {"tenant": "public"}
    # connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    # with Session(autocommit=False, autoflush=False, bind=connectable) as public_db:
    #     company = crud_auth.get_public_company_by_tenant_id(public_db, tenant_id)
    # if not company:
    #     raise HTTPException(status_code=400, detail="Unknown Company!")
    company = get_public_company_from_tenant(tenant_id)

    guide_uuid = str(uuid4())

    qr_code_id = crud_qr.generate_item_qr_id(db)
    qr_code_company = crud_qr.add_noise_to_qr(company.qr_id)

    qr_code_data = {
        "uuid": str(uuid4()),
        "resource": "guides",
        "resource_uuid": guide_uuid,
        "qr_code_id": qr_code_id,
        "qr_code_full_id": f"{qr_code_company}+{qr_code_id}",
        "ecc": "L",
        "created_at": datetime.now(timezone.utc),
    }

    new_qr_code = crud_qr.create_qr_code(db, qr_code_data)

    guide_data = {
        "uuid": guide_uuid,
        "author_id": auth_user.id,
        "name": guide.name,
        "text": description,
        "qr_code_id": new_qr_code.id,
        "text_json": guide.text_json,
        # "video_json": guide.video_json,
        # "video_id": guide.video_id,
        "files_guide": files,
        "created_at": datetime.now(timezone.utc),
    }

    if related_item is not None:
        guide_data["item"] = [db_item]

    new_guide = crud_guides.create_guide(db, guide_data)

    return new_guide


@guide_router.patch("/{guide_uuid}", response_model=GuideResponse)
def guide_edit(*, db: UserDB, guide_uuid: UUID, guide: GuideEditIn, auth_user: CurrentUser):
    db_guide = crud_guides.get_guide_by_uuid(db, guide_uuid)
    if not db_guide:
        raise HTTPException(status_code=400, detail="Item not found!")

    guide_data = guide.model_dump(exclude_unset=True)

    files = []
    if ("files" in guide_data) and (guide_data["files"] is not None):
        for file in db_guide.files_guide:
            db_guide.files_guide.remove(file)
        for file in guide_data["files"]:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

        guide_data["files_guide"] = files
        del guide_data["files"]

    if ("text_html" in guide_data) and (guide_data["text_html"] is not None):
        guide_data["text"] = BeautifulSoup(guide.text_html, "html.parser").get_text()

    guide_data["updated_at"] = datetime.now(timezone.utc)

    new_guide = crud_guides.update_guide(db, db_guide, guide_data)

    return new_guide


@guide_router.delete("/{guide_uuid}", response_model=StandardResponse)
def guide_delete(*, db: UserDB, guide_uuid: UUID, auth_user: CurrentUser):
    db_guide = crud_guides.get_guide_by_uuid(db, guide_uuid)

    if not db_guide:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_guide)
    db.commit()

    return {"ok": True}
