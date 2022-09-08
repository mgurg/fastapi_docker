from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import crud_permission
from app.db import get_db
from app.schemas.responses import RoleSummaryResponse, StandardResponse
from app.schemas.schemas import RolePermissionFull
from app.service.bearer_auth import has_token

permission_router = APIRouter()


@permission_router.get("/", response_model=list[RoleSummaryResponse])  # , response_model=Page[UserIndexResponse]
def role_get_all(*, db: Session = Depends(get_db), auth=Depends(has_token)):
    db_roles = crud_permission.get_roles(db)
    return db_roles


@permission_router.get("/{role_uuid}", response_model=RolePermissionFull)  # , response_model=Page[UserIndexResponse]
def role_get_all(*, db: Session = Depends(get_db), role_uuid: UUID, auth=Depends(has_token)):
    db_roles = crud_permission.get_roles_by_uuid(db, role_uuid)
    return db_roles


@permission_router.post("/", response_model=StandardResponse)  # , response_model=User , auth=Depends(has_token)
def role_add(*, db: Session = Depends(get_db), auth=Depends(has_token)):
    pass
