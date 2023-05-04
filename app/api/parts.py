from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import crud_parts
from app.db import get_db
from app.schemas.requests import PartCreateIn
from app.schemas.responses import PartResponse
from app.service.bearer_auth import has_token

part_router = APIRouter()


# @part_router.get("/", response_model=list[PartResponse])
# def parts_get_all(
#     *,
#     db: Session = Depends(get_db),
#     field: str = "name",
#     order: str = "asc",
#     is_hidden: bool | None = None,
#     auth=Depends(has_token),
# ):
#     if field not in ["name"]:
#         field = "name"

#     parts = crud_parts.get_parts(db, field, order, is_hidden)
#     return parts


@part_router.post("/", response_model=PartResponse)
def parts_add_one(*, db: Session = Depends(get_db), part: PartCreateIn, auth=Depends(has_token)):
    db_part = crud_parts.get_part_by_name(db, part.name)

    if db_part:
        raise HTTPException(status_code=400, detail="part name already exists")

    part_data = {
        "uuid": str(uuid4()),
        "name": part.name,
        "color": part.color,
        "icon": part.icon,
        "author_id": auth["user_id"],
        "created_at": datetime.now(timezone.utc),
    }

    part = crud_parts.create_part(db, part_data)

    return part


# @part_router.patch("/{part_uuid}", response_model=PartResponse)
# def parts_edit_one(*, db: Session = Depends(get_db), part_uuid: UUID, part: PartEditIn, auth=Depends(has_token)):
#     db_part = crud_parts.get_part_by_uuid(db, part_uuid)

#     part_data = {"is_hidden": part.is_hidden}
#     if part.color is not None:
#         part_data["color"] = part.color.as_hex()

#     crud_parts.update_part(db, db_part, part_data)
#     return db_part


# @part_router.delete("/{part_uuid}", response_model=StandardResponse)
# def parts_delete_one(
#     *, db: Session = Depends(get_db), part_uuid: UUID, force_delete: bool = False, auth=Depends(has_token)
# ):
#     db_part = crud_parts.get_part_by_uuid(db, part_uuid)

#     if not db_part:
#         raise HTTPException(status_code=404, detail="part not found")

#     part_usage = crud_issues.count_issues_by_part(db, db_part.id)

#     if part_usage > 0:
#         raise HTTPException(status_code=400, detail="part in use")

#     # print(part_usage)
#     db.delete(db_part)
#     db.commit()

#     return {"ok": True}
