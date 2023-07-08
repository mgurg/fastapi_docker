from datetime import datetime, timezone
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params, paginate
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session

from app.crud import crud_auth, crud_files, crud_guides, crud_items, crud_qr
from app.db import engine, get_db
from app.schemas.requests import GuideAddIn, GuideEditIn
from app.schemas.responses import GuideIndexResponse, GuideResponse, StandardResponse

# from app.schemas.schemas import GuideIndexResponse
from app.service.aws_s3 import generate_presigned_url
from app.service.bearer_auth import has_token

guide_router = APIRouter()


@guide_router.get("/", response_model=Page[GuideResponse])  #
def guide_get_all(
    *,
    db: Session = Depends(get_db),
    params: Params = Depends(),
    search: str = None,
    item_uuid: UUID | None = None,
    order: str = "asc",
    field: str = "name",
    auth=Depends(has_token),
):
    if field not in ["name"]:
        field = "name"

    item_id = None
    if item_uuid is not None:
        db_item = crud_items.get_item_by_uuid(db, item_uuid)
        if db_item is None:
            raise HTTPException(status_code=401, detail="Item not found")
        item_id = db_item.id

    db_guides = crud_guides.get_guides(db, search, item_id, field, order)
    return paginate(db_guides, params)


@guide_router.get("/{guide_uuid}", response_model=GuideIndexResponse)  # , response_model=Page[UserIndexResponse]
def guide_get_one(*, db: Session = Depends(get_db), guide_uuid: UUID, request: Request, auth=Depends(has_token)):
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
def guide_add(*, db: Session = Depends(get_db), request: Request, guide: GuideAddIn, auth=Depends(has_token)):
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

    company = None
    schema_translate_map = {"tenant": "public"}
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable) as public_db:
        company = crud_auth.get_public_company_by_tenant_id(public_db, tenant_id)
    if not company:
        raise HTTPException(status_code=400, detail="Unknown Company!")

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
        "author_id": auth["user_id"],
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
def guide_edit(*, db: Session = Depends(get_db), guide_uuid: UUID, guide: GuideEditIn, auth=Depends(has_token)):
    db_guide = crud_guides.get_guide_by_uuid(db, guide_uuid)
    if not db_guide:
        raise HTTPException(status_code=400, detail="Item not found!")

    guide_data = guide.dict(exclude_unset=True)

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
def guide_delete(*, db: Session = Depends(get_db), guide_uuid: UUID, auth=Depends(has_token)):
    db_guide = crud_guides.get_guide_by_uuid(db, guide_uuid)

    if not db_guide:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_guide)
    db.commit()

    return {"ok": True}
