from datetime import datetime, time, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import StandardResponse, UserIndexResponse, Users
from app.service.helpers import get_uuid
from app.service.password import Password

user_router = APIRouter()


@user_router.post("/add", response_model=StandardResponse, name="task:Tasks")
async def user_get_all(*, session: Session = Depends(get_session)):

    new_user = Users(
        client_id=3,
        email="tenant@t1.com",
        service_token="t" * 32,
        service_token_valid_to=datetime.now() + timedelta(days=1),
        password="p" * 256,
        user_role_id=2,
        created_at=datetime.utcnow(),
        is_active=False,
        tz="string",
        lang="string",
        uuid=get_uuid(),  # str(uuid.uuid4()),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)


@user_router.get("/index", response_model=List[UserIndexResponse], name="user:Profile")
async def user_get_all(*, session: Session = Depends(get_session)):
    users = session.exec(
        select(Users)
        .where(Users.client_id == 2)
        .where(Users.is_active == True)
        .where(Users.deleted_at == None)
        # .execution_options(schema_translate_map={None: "tenant_1"})
        # https://github.com/flowfelis/test-fast-api/blob/cb40311e08de10e3a4cf83881af6f36d11fdc4d9/app/main.py
    ).all()

    return users


@user_router.get("/{uuid}", response_model=UserIndexResponse, name="user:Profile")
async def user_get_all(*, session: Session = Depends(get_session), uuid):
    users = session.exec(
        select(Users)
        .where(Users.client_id == 2)
        .where(Users.uuid == uuid)
        .where(Users.is_active == True)
        .where(Users.deleted_at == None)
    ).first()
    return users
