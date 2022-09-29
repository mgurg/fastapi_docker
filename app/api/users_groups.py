from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import crud_groups
from app.db import get_db
from app.schemas.requests import GroupAddIn
from app.schemas.schemas import GroupAdd, RolePermissionFull
from app.service.bearer_auth import has_token

group_router = APIRouter()


@group_router.get("/")
def group_get_all(*, db: Session = Depends(get_db), auth=Depends(has_token)):
    db_roles = crud_groups.get_user_groups(db)
    return db_roles


@group_router.get("/{group_uuid}", response_model=RolePermissionFull)  # , response_model=Page[UserIndexResponse]
def group_get_one(*, db: Session = Depends(get_db), group_uuid: UUID, auth=Depends(has_token)):
    pass


@group_router.post("/", response_model=GroupAdd)
def group_add(*, db: Session = Depends(get_db), role: GroupAddIn, auth=Depends(has_token)):

    pass


# @group_router.patch("/{group_uuid}", response_model=RolePermissionFull)
# def group_edit(*, db: Session = Depends(get_db), group_uuid: UUID, role: RoleEditIn, auth=Depends(has_token)):

#     pass


# @group_router.delete("/{group_uuid}", response_model=StandardResponse)
# def group_delete(*, db: Session = Depends(get_db), group_uuid: UUID, auth=Depends(has_token)):

#     pass

#     return {"ok": True}
