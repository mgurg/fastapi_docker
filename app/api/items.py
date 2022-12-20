from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params, paginate
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session

from app.crud import crud_auth, crud_files, crud_items, crud_qr
from app.db import engine, get_db
from app.schemas.requests import ItemAddIn, ItemEditIn
from app.schemas.responses import ItemIndexResponse, ItemResponse, StandardResponse
from app.service.aws_s3 import generate_presigned_url
from app.service.bearer_auth import has_token

item_router = APIRouter()


@item_router.get("/", response_model=Page[ItemIndexResponse])
def item_get_all(
    *,
    db: Session = Depends(get_db),
    params: Params = Depends(),
    search: str = None,
    sortOrder: str = "asc",
    sortColumn: str = "name",
    auth=Depends(has_token),
):

    sortTable = {"name": "name"}

    db_items = crud_items.get_items(db, search, sortTable[sortColumn], sortOrder)
    return paginate(db_items, params)


@item_router.get("/{item_uuid}", response_model=ItemResponse)  # , response_model=Page[UserIndexResponse]
def item_get_one(*, db: Session = Depends(get_db), item_uuid: UUID, request: Request, auth=Depends(has_token)):
    db_item = crud_items.get_item_by_uuid(db, item_uuid)

    try:
        for picture in db_item.files_item:
            picture.url = generate_presigned_url(
                request.headers.get("tenant", "public"),
                "_".join([str(picture.uuid), picture.file_name]),
            )
    except Exception as e:
        capture_exception(e)

    return db_item


@item_router.post("/", response_model=ItemIndexResponse)
def item_add(*, db: Session = Depends(get_db), request: Request, item: ItemAddIn, auth=Depends(has_token)):

    tenant_id = request.headers.get("tenant", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Unknown Company!")

    company = None
    schema_translate_map = dict(tenant="public")
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable) as public_db:
        company = crud_auth.get_public_company_by_tenant_id(public_db, tenant_id)
    if not company:
        raise HTTPException(status_code=400, detail="Unknown Company!")

    files = []
    if item.files is not None:
        for file in item.files:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

    item_uuid = str(uuid4())

    qr_code_id = crud_qr.generate_item_qr_id(db)
    qr_code_company = crud_qr.add_noise_to_qr(company.qr_id)

    qr_code_data = {
        "uuid": str(uuid4()),
        "resource": "items",
        "qr_code_id": qr_code_id,
        "qr_code_content": f"{qr_code_company}+{qr_code_id}",
        "ecc": "L",
        "created_at": datetime.now(timezone.utc),
        "resource_uuid": item_uuid,
    }

    # print("############################")
    # print(qr_code_data)
    # raise HTTPException(status_code=400, detail="Unknown Company!")
    new_qr_code = crud_qr.create_qr_code(db, qr_code_data)

    item_data = {
        "uuid": item_uuid,
        "name": item.name,
        "description": item.description,
        "description_jsonb": item.description_jsonb,
        "qr_code_id": new_qr_code.id,
        "files_item": files,
        "created_at": datetime.now(timezone.utc),
    }

    new_item = crud_items.create_item(db, item_data)

    return new_item


@item_router.patch("/{item_uuid}", response_model=ItemIndexResponse)
def item_edit(*, db: Session = Depends(get_db), item_uuid: UUID, role: ItemEditIn, auth=Depends(has_token)):

    db_item = crud_items.get_item_by_uuid(db, item_uuid)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found!")

    item_data = role.dict(exclude_unset=True)

    files = []
    if ("files" in item_data) and (item_data["files"] is not None):
        for file in db_item.files_item:
            db_item.files_item.remove(file)
        for file in item_data["files"]:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

        item_data["files_item"] = files
        del item_data["files"]

    item_data["updated_at"] = datetime.now(timezone.utc)

    new_item = crud_items.update_item(db, db_item, item_data)

    return new_item


@item_router.delete("/{item_uuid}", response_model=StandardResponse)
def item_delete(*, db: Session = Depends(get_db), item_uuid: UUID, auth=Depends(has_token)):

    db_qr = crud_qr.get_qr_code_by_resource_uuid(db, item_uuid)
    db_item = crud_items.get_item_by_uuid(db, item_uuid)

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.delete(db_qr)
    db.commit()

    return {"ok": True}
