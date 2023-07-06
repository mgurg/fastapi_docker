from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate
from sqlalchemy.orm import Session

from app.crud import crud_groups, crud_users
from app.db import get_db
from app.models.models import User
from app.schemas.requests import GroupAddIn, GroupEditIn
from app.schemas.responses import GroupResponse, GroupSummaryResponse, StandardResponse
from app.service.bearer_auth import has_token

group_router = APIRouter()

CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[Session, Depends(get_db)]


@group_router.get("/", response_model=Page[GroupSummaryResponse])
def group_get_all(
    *,
    db: UserDB,
    params: Annotated[Params, Depends()],
    auth_user: CurrentUser,
    search: str = None,
    field: str = "name",
    order: str = "asc",
):
    if field not in ["name", "created_at"]:
        field = "name"

    db_user_groups = crud_groups.get_user_groups(db, search, field, order)
    return paginate(db_user_groups, params)


@group_router.get("/{group_uuid}", response_model=GroupResponse)
def group_get_one(*, db: UserDB, group_uuid: UUID, auth_user: CurrentUser):
    db_user_group = crud_groups.get_user_group_by_uuid(db, group_uuid)

    return db_user_group


@group_router.post("/", response_model=GroupResponse)
def group_add(*, db: UserDB, group: GroupAddIn, auth_user: CurrentUser):
    db_user_group = crud_groups.get_user_group_by_name(db, group.name)
    if db_user_group:
        raise HTTPException(status_code=400, detail="Group already exists!")

    users = []
    if group.users is not None:
        for user_uuid in group.users:
            db_user = crud_users.get_user_by_uuid(db, user_uuid)
            if db_user:
                users.append(db_user)

    group_data = {
        "uuid": str(uuid4()),
        "name": group.name,
        "description": group.description,
        "symbol": group.symbol,
        "users": users,
        "created_at": datetime.now(timezone.utc),
    }

    new_group = crud_groups.create_group_with_users(db, group_data)

    return new_group


@group_router.patch("/{group_uuid}", response_model=GroupResponse)
def group_edit(*, db: UserDB, group_uuid: UUID, role: GroupEditIn, auth_user: CurrentUser):
    db_user_group = crud_groups.get_user_group_by_uuid(db, group_uuid)
    if not db_user_group:
        raise HTTPException(status_code=400, detail="Group not found exists!")

    group_data = role.dict(exclude_unset=True)

    users = []
    if ("users" in group_data) and (group_data["users"] is not None):
        for user in db_user_group.users:
            db_user_group.users.remove(user)
        for user in group_data["users"]:
            db_permission = crud_users.get_user_by_uuid(db, user)
            if db_permission:
                users.append(db_permission)

        del group_data["users"]
        group_data["users"] = users

    new_group = crud_groups.update_user_group(db, db_user_group, group_data)

    return new_group


@group_router.delete("/{group_uuid}", response_model=StandardResponse)
def group_delete(*, db: UserDB, group_uuid: UUID, auth_user: CurrentUser):
    db_user_group = crud_groups.get_user_group_by_uuid(db, group_uuid)

    if not db_user_group:
        raise HTTPException(status_code=404, detail="Group not found")

    # TODO rel?
    db.delete(db_user_group)
    db.commit()

    return {"ok": True}
