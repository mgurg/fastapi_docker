from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import StandardResponse, UserIndexResponse, Users
from app.service.password import Password

user_router = APIRouter()


# @user_router.post("/add", response_model=StandardResponse, name="user:add")
# async def user_add(*, session: Session = Depends(get_session), user: UserCreateIn):

#     res = UserCreateIn.from_orm(user)
#     db_user = session.exec(select(Users).where(Users.email == res.email).where(Users.deleted_at == None)).one_or_none()
#     if db_user:
#         raise HTTPException(status_code=404, detail="User already exists!")

#     password = Password(res.password)
#     is_password_ok = password.compare(res.password_confirmation)

#     if is_password_ok is True:
#         pass_hash = argon2.hash(res.password)
#     else:
#         raise HTTPException(status_code=400, detail=is_password_ok)

#     new_user = Users(
#         client_id=1,
#         email="mail@mail.com",
#     )

#     session.add(new_user)
#     session.commit()
#     session.refresh(new_user)

#     return {"ok": True}


@user_router.get("/index", response_model=List[UserIndexResponse], name="user:Profile")
async def user_get_all(*, session: Session = Depends(get_session)):
    users = session.exec(select(Users).where(Users.client_id == 2).where(Users.deleted_at == None)).all()
    return users


@user_router.get("/{uuid}", response_model=UserIndexResponse, name="user:Profile")
async def user_get_all(*, session: Session = Depends(get_session), uuid):
    users = session.exec(
        select(Users).where(Users.client_id == 2).where(Users.uuid == uuid).where(Users.deleted_at == None)
    ).first()
    return users
