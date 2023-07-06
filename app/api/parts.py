from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import crud_issues, crud_parts
from app.db import get_db
from app.models.models import User
from app.schemas.requests import PartCreateIn, PartEditIn
from app.schemas.responses import PartResponse, StandardResponse
from app.service.bearer_auth import has_token

part_router = APIRouter()
CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[Session, Depends(get_db)]


@part_router.get("/issue/{issue_uuid}", response_model=list[PartResponse])
def parts_get_all(
    *,
    db: UserDB,
    issue_uuid: UUID,
    auth_user: CurrentUser,
    field: str = "name",
    order: str = "asc",
    is_hidden: bool | None = None,
):
    if field not in ["name"]:
        field = "name"

    issue = crud_issues.get_issue_by_uuid(db, issue_uuid)

    parts = crud_parts.get_parts(db, issue.id)
    return parts


@part_router.post("/", response_model=PartResponse)
def parts_add_one(*, db: UserDB, part: PartCreateIn, auth_user: CurrentUser):
    db_issue = crud_issues.get_issue_by_uuid(db, part.issue_uuid)

    if not db_issue:
        raise HTTPException(status_code=400, detail="Issue not found")

    value = part.value
    if not value:
        value = part.price * part.quantity

    part_data = {
        "uuid": str(uuid4()),
        "issue_id": db_issue.id,
        "author_id": auth_user.id,
        "name": part.name,
        "description": part.description,
        "price": part.price,
        "quantity": part.quantity,
        "unit": part.unit,
        "value": value,
        "created_at": datetime.now(timezone.utc),
    }

    if db_issue.item_id:
        part_data["item_id"] = db_issue.item_id

    # pprint(part_data)
    # return db_issue

    new_part = crud_parts.create_part(db, part_data)

    return new_part


@part_router.patch("/{part_uuid}", response_model=PartResponse)
def parts_edit_one(*, db: UserDB, part_uuid: UUID, part: PartEditIn, auth_user: CurrentUser):
    db_part = crud_parts.get_part_by_uuid(db, part_uuid)

    if not db_part:
        raise HTTPException(status_code=400, detail="Part not found")

    price = part.price
    quantity = part.quantity
    value = part.value

    if not price:
        price = db_part.price

    if not quantity:
        quantity = db_part.quantity

    if not value:
        value = price * quantity

    part_data = part.dict(exclude_unset=True)
    part_data["price"] = price
    part_data["quantity"] = quantity
    part_data["value"] = value

    # pprint(part_data)

    updated_part = crud_parts.update_part(db, db_part, part_data)
    return updated_part


@part_router.delete("/{part_uuid}", response_model=StandardResponse)
def parts_delete_one(*, db: UserDB, part_uuid: UUID, auth_user: CurrentUser, force_delete: bool = False):
    db_part = crud_parts.get_part_by_uuid(db, part_uuid)

    if not db_part:
        raise HTTPException(status_code=404, detail="part not found")

    db.delete(db_part)
    db.commit()

    return {"ok": True}
