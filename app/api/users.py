from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params, paginate
from sqlalchemy.orm import Session

from app.crud import crud_users
from app.db import get_db
from app.schemas.requests import UserCreateIn
from app.schemas.responses import StandardResponse, UserIndexResponse
from app.service.bearer_auth import has_token
from app.service.password import Password

user_router = APIRouter()


@user_router.get("/", response_model=Page[UserIndexResponse])
def user_get_all(*, db: Session = Depends(get_db), params: Params = Depends(), auth=Depends(has_token)):
    db_users = crud_users.get_users(db)
    return paginate(db_users, params)


@user_router.get("/{user_uuid}", response_model=UserIndexResponse)
async def user_get_one(*, db: Session = Depends(get_db), user_uuid: UUID, auth=Depends(has_token)):
    user = crud_users.get_user_by_uuid(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.post("/", response_model=StandardResponse)  # , response_model=User , auth=Depends(has_token)
def read_user(*, db: Session = Depends(get_db), user: UserCreateIn, request: Request, auth=Depends(has_token)):

    db_user = crud_users.get_user_by_email(db, user.email)
    if db_user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    if (user.password is None) or (user.password_confirmation is None):
        raise HTTPException(status_code=400, detail="Password is missing")

    password = Password(user.password)
    is_password_ok = password.compare(user.password_confirmation)

    if is_password_ok is not True:
        raise HTTPException(status_code=400, detail=is_password_ok)

    user_data = user.dict(exclude_unset=True)
    user_data.pop("password_confirmation", None)

    user_data["uuid"] = str(uuid4())
    user_data["password"] = password.hash()
    user_data["tos"] = True
    user_data["is_active"] = True
    user_data["is_verified"] = True
    user_data["user_role_id"] = 1
    user_data["tenant_id"] = request.headers.get("tenant", "public")
    user_data["tos"] = True
    user_data["tz"] = "Europe/Warsaw"
    user_data["lang"] = "pl"
    user_data["created_at"] = datetime.utcnow()

    crud_users.create_user(db, user_data)

    return {"ok": True}


@user_router.patch("/{user_uuid}", response_model=StandardResponse)
async def user_edit(*, db: Session = Depends(get_db), user_uuid: UUID, user: UserCreateIn, auth=Depends(has_token)):
    db_user = crud_users.get_user_by_uuid(db, user_uuid)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.dict(exclude_unset=True)

    if "password" in user_data.keys():
        password = Password(user_data["password"])
        is_password_ok = password.compare(user_data["password_confirmation"])

        if is_password_ok is not True:
            raise HTTPException(status_code=400, detail=is_password_ok)

        user_data["password"] = password.hash()
        user_data["updated_at"] = datetime.utcnow()
        user_data.pop("password_confirmation", None)

    crud_users.update_user(db, db_user, user_data)

    return {"ok": True}


@user_router.delete("/{user_uuid}", response_model=StandardResponse)
async def user_get_all(*, db: Session = Depends(get_db), user_uuid: UUID, auth=Depends(has_token)):

    db_user = crud_users.get_user_by_uuid(db, user_uuid)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()

    return {"ok": True}
