import secrets
import uu
from datetime import datetime, timedelta

from disposable_email_domains import blocklist
from fastapi import APIRouter, Depends, HTTPException, Request
from passlib.hash import argon2
from pydantic import EmailStr
from sqlalchemy import func
from sqlmodel import Session, select
from stdnum.pl import nip
from user_agents import parse

from app.config import get_settings
from app.db import get_session
from app.models.models import (
    Accounts,
    LoginHistory,
    StandardResponse,
    UserActivateOut,
    UserFirstRunIn,
    UserLoginIn,
    UserLoginOut,
    UserRegisterIn,
    Users,
    UserSetPassIn,
)
from app.service.helpers import get_uuid
from app.service.notification import EmailNotification
from app.service.password import Password

register_router = APIRouter()
settings = get_settings()


@register_router.post("/add", response_model=StandardResponse)
async def auth_register(*, session: Session = Depends(get_session), users: UserRegisterIn):
    """Register a new user (company). New account requires activation."""

    res = UserRegisterIn.from_orm(users)

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

    account_id = session.exec(select([func.max(Users.account_id)])).one()
    if account_id is None:
        account_id = 0

    # TODO: TOS field
    new_user = Users(
        account_id=account_id + 2,
        email=res.email.strip(),
        service_token=secrets.token_hex(32),
        service_token_valid_to=datetime.utcnow() + timedelta(days=1),
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


@register_router.post("/first_run")
async def auth_first_run(*, session: Session = Depends(get_session), user: UserFirstRunIn):
    """Activate user based on service token"""

    res = UserFirstRunIn.from_orm(user)

    if not nip.is_valid(res.nip):  # 123-456-32-18
        raise HTTPException(status_code=404, detail="Invalid NIP number")

    db_user = session.exec(
        select(Users)
        .where(Users.service_token == res.token)
        .where(Users.is_active == False)
        .where(Users.service_token_valid_to > datetime.utcnow())
        .where(Users.deleted_at.is_(None))
    ).one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    token = secrets.token_hex(64)

    update_package = {
        "first_name": res.first_name,
        "last_name": res.last_name,
        "is_active": True,
        "service_token": None,
        "service_token_valid_to": None,
        "auth_token": token,
        "auth_token_valid_to": datetime.utcnow() + timedelta(days=1),
        "updated_at": datetime.utcnow(),
    }

    # !TODO: Save NIP in customers table
    # url = "https://rejestr.io/api/v1/krs/28860"
    # payload={}
    # headers = {
    #   'Authorization': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    # }
    # response = requests.request("GET", url, headers=headers, data=payload)
    # print(response.text)

    for key, value in update_package.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # account = Accounts(uuid=get_uuid(), account_id=db_user.account_id)

    # session.add(account)
    # session.commit()
    # session.refresh(account)

    return {
        "ok": True,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "lang": db_user.lang,
        "tz": db_user.tz,
        "token": token,
    }


@register_router.post("/login", response_model=UserLoginOut)
async def auth_login(*, session: Session = Depends(get_session), users: UserLoginIn, req: Request):
    ip_info = "NO_INFO"  # get_ip_info(ip_addr)
    ua_string = req.headers["User-Agent"]
    user_agent = parse(ua_string)
    browser_lang = req.headers["accept-language"]

    try:
        res = UserLoginIn.from_orm(users)
        db_user = session.exec(
            select(Users)
            .where(Users.email == res.email)
            .where(Users.is_active == True)
            .where(Users.deleted_at.is_(None))
        ).one_or_none()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if argon2.verify(res.password, db_user.password):
            token = secrets.token_hex(64)
        else:
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        token_valid_to = datetime.utcnow() + timedelta(days=1)
        if res.permanent is True:
            token_valid_to = datetime.utcnow() + timedelta(days=30)

        update_package = {
            "auth_token": secrets.token_hex(64),  # token,
            "auth_token_valid_to": token_valid_to,
            "updated_at": datetime.utcnow(),
        }

        for key, value in update_package.items():
            setattr(db_user, key, value)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        # login_history = LoginHistory(
        #     user_id=db_user.id,
        #     login_date=datetime.utcnow(),
        #     os=user_agent.os.family,
        #     browser=user_agent.browser.family,
        #     browser_lang=browser_lang,
        #     ip_address=req.client.host,
        #     user_agent=ua_string,
        #     ipinfo=ip_info,
        # )

    except Exception as err:
        # login_history = LoginHistory(
        #     login_date=datetime.utcnow(),
        #     failed_login=res.email,
        #     failed_passwd=res.password,
        #     ip_address=req.client.host,
        # )
        # session.add(login_history)
        # session.commit()
        # session.refresh(login_history)
        raise HTTPException(status_code=404, detail="User not found")

    email = EmailNotification(settings.email_labs_app_key, settings.email_labs_secret_key)

    receiver = settings.email_dev

    template_data = {  # Template: fb45d7d0
        "name": "Jan",
        "product_name": "Intio",
        "login_url": "https://remontmaszyn.pl/login",
        "username": receiver,
        "sender_name": "Michał",
        "action_url": "https://remontmaszyn.pl/asdf234",
    }
    email.send(settings.email_sender, receiver, "Greetings from AWS!", "fb45d7d0", template_data)

    return db_user


@register_router.get("/verify/{token}", response_model=StandardResponse)
async def auth_verify(*, session: Session = Depends(get_session), token: str):
    user_db = session.exec(
        select(Users)
        .where(Users.auth_token == token)
        .where(Users.is_active == True)
        .where(Users.auth_token_valid_to > datetime.utcnow())
        .where(Users.deleted_at.is_(None))
    ).one_or_none()
    if user_db is None:
        raise HTTPException(status_code=404, detail="Invalid token")
    return {"ok": True}


@register_router.get("/remind-password/{user_email}", response_model=StandardResponse)
async def auth_remind(*, session: Session = Depends(get_session), user_email: EmailStr):
    db_user = session.exec(
        select(Users).where(Users.email == user_email).where(Users.is_active == True).where(Users.deleted_at.is_(None))
    ).one_or_none()
    if db_user is None:
        return {"ok": True}
        # raise HTTPException(status_code=404, detail="Invalid email")

    update_package = {
        "service_token": secrets.token_hex(32),
        "service_token_valid_to": datetime.utcnow() + timedelta(days=1),
        "updated_at": datetime.utcnow(),
    }

    for key, value in update_package.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # postmark = PostmarkClient(server_token=settings.api_postmark)
    # postmark.emails.send(
    #     From='sender@example.com',
    #     To='recipient@example.com',
    #     Subject='Postmark test',
    #     HtmlBody='HTML body goes here'
    # )

    return {"ok": True}


@register_router.post("/set-password/", response_model=StandardResponse)
async def auth_set_password(*, session: Session = Depends(get_session), user: UserSetPassIn):
    res = UserSetPassIn.from_orm(user)

    db_user = session.exec(
        select(Users)
        .where(Users.service_token == res.token)
        .where(Users.is_active == True)
        .where(Users.service_token_valid_to > datetime.utcnow())
        .where(Users.deleted_at.is_(None))
    ).one_or_none()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Invalid email")

    password = Password(res.password)
    is_password_ok = password.compare(res.password_confirmation)

    if is_password_ok is True:
        pass_hash = argon2.hash(res.password)
    else:
        raise HTTPException(status_code=400, detail=is_password_ok)

    update_package = {
        "password": pass_hash,
        "auth_token": None,
        "service_token": None,
        "service_token_valid_to": None,
        "updated_at": datetime.utcnow(),
    }

    for key, value in update_package.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return {"ok": True}
