from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate
from sqlalchemy.orm import Session

from app.crud import crud_items
from app.db import get_db
from app.schemas.requests import ItemAddIn, ItemEditIn
from app.schemas.responses import ItemResponse, StandardResponse
from app.service.bearer_auth import has_token

item_router = APIRouter()


@item_router.get("/", response_model=Page[ItemResponse])
def item_get_all(
    *,
    db: Session = Depends(get_db),
    params: Params = Depends(),
    search: str = None,
    sortOrder: str = "asc",
    sortColumn: str = "name",
    auth=Depends(has_token)
):

    sortTable = {"name": "name"}

    db_items = crud_items.get_items(db, search, sortTable[sortColumn], sortOrder)
    return paginate(db_items, params)


@item_router.get("/{item_uuid}", response_model=ItemResponse)  # , response_model=Page[UserIndexResponse]
def item_get_one(*, db: Session = Depends(get_db), item_uuid: UUID, auth=Depends(has_token)):
    db_item = crud_items.get_item_by_uuid(db, item_uuid)

    return db_item


@item_router.post("/", response_model=ItemResponse)
def item_add(*, db: Session = Depends(get_db), item: ItemAddIn, auth=Depends(has_token)):

    item_data = {
        "uuid": str(uuid4()),
        "name": item.name,
        "description": item.description,
        "description_jsonb": item.description_jsonb,
        "created_at": datetime.now(timezone.utc),
    }

    new_item = crud_items.create_item(db, item_data)

    return new_item


@item_router.patch("/{item_uuid}", response_model=ItemResponse)
def item_edit(*, db: Session = Depends(get_db), item_uuid: UUID, role: ItemEditIn, auth=Depends(has_token)):

    db_item = crud_items.get_item_by_uuid(db, item_uuid)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found!")

    item_data = role.dict(exclude_unset=True)
    item_data["updated_at"] = datetime.now(timezone.utc)

    new_item = crud_items.update_item(db, db_item, item_data)

    return new_item


@item_router.delete("/{item_uuid}", response_model=StandardResponse)
def item_delete(*, db: Session = Depends(get_db), item_uuid: UUID, auth=Depends(has_token)):

    db_item = crud_items.get_item_by_uuid(db, item_uuid)

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()

    return {"ok": True}
