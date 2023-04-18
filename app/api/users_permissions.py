from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate
from sqlalchemy.orm import Session

from app.crud import crud_permission, crud_users
from app.db import get_db
from app.schemas.requests import RoleAddIn, RoleEditIn
from app.schemas.responses import PermissionResponse, RolePermissionFull, RoleSummaryResponse, StandardResponse
from app.service.bearer_auth import has_token

permission_router = APIRouter()


@permission_router.get("/", response_model=Page[RoleSummaryResponse])  # , response_model=Page[UserIndexResponse]
def role_get_all(
    *,
    db: Session = Depends(get_db),
    params: Params = Depends(),
    search: str = None,
    all: bool = True,
    sortOrder: str = "asc",
    sortColumn: str = "name",
    auth=Depends(has_token),
):
    sortTable = {"name": "role_title"}

    db_roles = crud_permission.get_roles_summary(db, search, all, sortTable[sortColumn], sortOrder)
    return paginate(db_roles, params)


@permission_router.get("/all", response_model=list[PermissionResponse])
def permissions_get_all(*, db: Session = Depends(get_db), auth=Depends(has_token)):
    db_permissions = crud_permission.get_permissions(db)
    return db_permissions


@permission_router.get("/{role_uuid}", response_model=RolePermissionFull)  # , response_model=Page[UserIndexResponse]
def role_get_one(*, db: Session = Depends(get_db), role_uuid: UUID, auth=Depends(has_token)):
    db_roles = crud_permission.get_role_by_uuid(db, role_uuid)
    if not db_roles:
        raise HTTPException(status_code=400, detail="Role already exists!")
    return db_roles


@permission_router.post("/", response_model=RolePermissionFull)
def role_add(*, db: Session = Depends(get_db), role: RoleAddIn, auth=Depends(has_token)):
    db_role = crud_permission.get_role_by_name(db, role.title)
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists!")

    permissions = []
    if role.permissions is not None:
        for permissions_uuid in role.permissions:
            db_permission = crud_permission.get_permission_by_uuid(db, permissions_uuid)
            if db_permission:
                permissions.append(db_permission)

    role_data = {
        "uuid": str(uuid4()),
        "is_custom": True,
        "is_visible": True,
        "role_name": role.title,
        "role_title": role.title,
        "role_description": role.description,
        "permission": permissions,
    }

    new_role = crud_permission.create_role_with_permissions(db, role_data)
    return new_role


@permission_router.patch("/{role_uuid}", response_model=RolePermissionFull)
def role_edit(*, db: Session = Depends(get_db), role_uuid: UUID, role: RoleEditIn, auth=Depends(has_token)):
    db_role = crud_permission.get_role_by_uuid(db, role_uuid)
    if not db_role:
        raise HTTPException(status_code=400, detail="Role already exists!")

    role_data = role.dict(exclude_unset=True)

    permissions = []
    if ("permissions" in role_data) and (role_data["permissions"] is not None):
        for permission in db_role.permission:
            db_role.permission.remove(permission)
        for permission in role_data["permissions"]:
            db_permission = crud_permission.get_permission_by_uuid(db, permission)
            if db_permission:
                permissions.append(db_permission)

        role_data["permission"] = permissions
        del role_data["permissions"]

    role_data["role_name"] = role.title
    role_data["role_title"] = role.title
    role_data["role_description"] = role.description

    del role_data["title"]
    del role_data["description"]

    new_role = crud_permission.update_role(db, db_role, role_data)

    return new_role


@permission_router.delete("/{role_uuid}", response_model=StandardResponse)
def role_delete(*, db: Session = Depends(get_db), role_uuid: UUID, auth=Depends(has_token)):
    db_role = crud_permission.get_role_by_uuid(db, role_uuid)

    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    db_users = crud_users.get_users_by_role_id(db, db_role.id)
    # fields = ['uuid', 'first_name', 'last_name']
    # db_users_list = [dict(zip(fields, d)) for d in db_users]

    if db_users:
        error_message = {"message": "Permission assigned to One or more users", "count": len(db_users)}
        raise HTTPException(status_code=400, detail=error_message)

    db.delete(db_role)
    db.commit()

    return {"ok": True}
