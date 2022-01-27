import secrets
from datetime import datetime, timedelta

from disposable_email_domains import blocklist
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.hash import argon2
from sqlalchemy import false, func
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import StandardResponse, UserRegisterIn, Users
from app.service.helpers import get_uuid
from app.service.password import Password

register_router = APIRouter()


@register_router.post("/add", response_model=StandardResponse)
async def auth_register(*, session: Session = Depends(get_session), users: UserRegisterIn):
    res = UserRegisterIn.from_orm(users)
    # TODO: Trim input data, save if rules accepted on backend

    if res.email.strip().split("@")[1] in blocklist:
        raise HTTPException(status_code=400, detail="Temporary email not allowed")

    db_user_cnt = session.exec(select([func.count(Users.email)]).where(Users.email == res.email)).one()
    if db_user_cnt != 0:
        raise HTTPException(status_code=400, detail="User already exists")

    password = Password(res.password)
    is_password_ok = password.compare(res.password_confirmation)

    if is_password_ok is True:
        pass_hash = argon2.hash(res.password)
    else:
        raise HTTPException(status_code=400, detail=is_password_ok)

    client_id = session.exec(select([func.max(Users.client_id)])).one()
    if client_id is None:
        client_id = 0

    new_user = Users(
        client_id=client_id + 2,
        email=res.email.strip(),
        service_token=secrets.token_hex(32),
        service_token_valid_to=datetime.now() + timedelta(days=1),
        password=pass_hash,
        user_role_id=2,
        created_at=datetime.utcnow(),
        is_active=False,
        tz=res.tz,
        lang=res.lang,
        uuid=get_uuid(),  # str(uuid.uuid4()),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # postmark = PostmarkClient(server_token=settings.api_postmark)
    # postmark.emails.send(
    #     From='sender@example.com',
    #     To='recipient@example.com',
    #     Subject='Postmark test',
    #     HtmlBody='HTML body goes here'
    # )

    return {"ok": True}


@register_router.get("/users", name="user:Profile")
async def user_get_all(*, session: Session = Depends(get_session)):
    users = session.exec(select(Users)).all()
    return users
