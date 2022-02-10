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
