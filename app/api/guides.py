from datetime import datetime, timezone
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params, paginate
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session

from app.crud import crud_files, crud_guides, crud_items
from app.db import get_db
from app.schemas.requests import GuideAddIn, GuideEditIn
from app.schemas.responses import GuideResponse, StandardResponse
from app.schemas.schemas import GuideIndexResponse
from app.service.aws_s3 import generate_presigned_url
from app.service.bearer_auth import has_token

guide_router = APIRouter()


@guide_router.get("/", response_model=Page[GuideResponse])  #
def guide_get_all(
    *,
    db: Session = Depends(get_db),
    params: Params = Depends(),
    search: str = None,
    sortOrder: str = "asc",
    sortColumn: str = "name",
    auth=Depends(has_token)
):

    sortTable = {"name": "name"}

    db_guides = crud_guides.get_guides(db, search, sortTable[sortColumn], sortOrder)
    return paginate(db_guides, params)


@guide_router.get("/item/{item_uuid}", response_model=Page[GuideResponse])
def guides_get_by_item(
    *, db: Session = Depends(get_db), item_uuid: UUID, params: Params = Depends(), auth=Depends(has_token)
):

    db_item = crud_items.get_item_by_uuid(db, item_uuid)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_guides = crud_guides.get_guide_by_item_id(db, db_item.id)

    return paginate(db_guides, params)


@guide_router.get("/{guide_uuid}", response_model=GuideIndexResponse)  # , response_model=Page[UserIndexResponse]
def guide_get_one(*, db: Session = Depends(get_db), guide_uuid: UUID, request: Request, auth=Depends(has_token)):
    db_guide = crud_guides.get_guide_by_uuid(db, guide_uuid)

    if not db_guide:
        raise HTTPException(status_code=400, detail="Guide not found!")

    try:
        for picture in db_guide.files_guide:
            picture.url = generate_presigned_url(
                request.headers.get("tenant", "public"),
                "_".join([str(picture.uuid), picture.file_name]),
            )
    except Exception as e:
        capture_exception(e)

    return db_guide


@guide_router.post("/", response_model=GuideResponse)
def guide_add(*, db: Session = Depends(get_db), guide: GuideAddIn, auth=Depends(has_token)):

    db_item = crud_items.get_item_by_uuid(db, guide.item_uuid)
    if not db_item:
        raise HTTPException(status_code=400, detail="Related Item not found!")

    files = []
    if guide.files is not None:
        for file in guide.files:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

    html = guide.text_html
    soup = BeautifulSoup(html, "html.parser")
    description = soup.get_text()

    # json.dumps(guide.text_json)

    guide_data = {
        "uuid": str(uuid4()),
        "name": guide.name,
        "text": description,
        "text_jsonb": guide.text_json,  # TODO -> to text_json
        "video_jsonb": guide.video_jsonb,
        "video_id": guide.video_id,
        "files_guide": files,
        "item": [db_item],
        "created_at": datetime.now(timezone.utc),
    }

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
