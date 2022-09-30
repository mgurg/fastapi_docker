from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import crud_groups
from app.db import get_db
from app.schemas.requests import GroupAddIn
from app.schemas.responses import GroupResponse, GroupSummaryResponse
from app.schemas.schemas import GroupAdd, RolePermissionFull
from app.service.bearer_auth import has_token

group_router = APIRouter()


@group_router.get("/", response_model=list[GroupSummaryResponse])
def group_get_all(*, db: Session = Depends(get_db), auth=Depends(has_token)):
    db_user_groups = crud_groups.get_user_groups(db)
    return db_user_groups


@group_router.get("/{group_uuid}", response_model=GroupResponse)  # , response_model=Page[UserIndexResponse]
def group_get_one(*, db: Session = Depends(get_db), group_uuid: UUID, auth=Depends(has_token)):
    db_user_group = crud_groups.get_user_group_by_uuid(db, group_uuid)

    return db_user_group


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
