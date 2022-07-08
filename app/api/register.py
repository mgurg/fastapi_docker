import random
import re
import secrets
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytz
from disposable_email_domains import blocklist
from fastapi import APIRouter, Depends, HTTPException, Request
from langcodes import standardize_tag
from passlib.hash import argon2
from pydantic import EmailStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# from sqlmodel import Session, select
from stdnum.pl import nip
from user_agents import parse

from app.config import get_settings
from app.db import get_session
from app.model.model import Account, User

# from app.models.models import (
#     Accounts,
#     LoginHistory,
#     UserActivateOut,
#     UserFirstRunIn,
#     UserLoginIn,
#     UserLoginOut,
#     UserRegisterIn,
#     Users,
#     UserSetPassIn,
# )
from app.schema.schema import (
    StandardResponse,
    UserFirstRunIn,
    UserLoginIn,
    UserLoginOut,
    UserRegisterIn,
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

    db_user = session.execute(select(User.email).where(User.email == res.email)).scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    is_password_ok = Password(res.password).compare(res.password_confirmation)

    if is_password_ok is True:
        pass_hash = argon2.hash(res.password)
    else:
        raise HTTPException(status_code=400, detail=is_password_ok)

    if res.tz not in pytz.all_timezones_set:
        raise HTTPException(status_code=400, detail="Invalid timezone")

    confirmation_token = secrets.token_hex(32)
    new_user = User(
        account_id=0,
        email=res.email.strip(),
        service_token=confirmation_token,
        service_token_valid_to=datetime.utcnow() + timedelta(days=1),
        password=pass_hash,
        user_role_id=1,  # 1 - SU_ADMIN / 2 - USER / 3 - VIEWER
        created_at=datetime.utcnow(),
        is_active=False,
        is_verified=False,
        tos=res.tos,
        tz=res.tz,
        lang=standardize_tag(res.lang),
        uuid=str(uuid4()),
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Notification {"mode": settings.environment}
    # email = EmailNotification(settings.email_labs_app_key, settings.email_labs_secret_key, settings.email_smtp)
    # receiver = res.email.strip()

    # template_data = {  # Template: 4b4653ba 	RegisterAdmin_PL
    #     "product_name": "Intio",
    #     "login_url": "https://beta.remontmaszyn.pl/login",
    #     "username": receiver,
    #     "sender_name": "Michał",
    #     "action_url": "https://beta.remontmaszyn.pl/activate/" + confirmation_token,
    # }
    # email.send(settings.email_sender, receiver, "[Intio] Poprawmy coś razem!", "4b4653ba", template_data)

    return {"ok": True}


@register_router.post("/first_run")
async def auth_first_run(*, session: Session = Depends(get_session), user: UserFirstRunIn):
    """Activate user based on service token"""

    res = UserFirstRunIn.from_orm(user)
    nipId = re.sub("[^0-9]", "", res.nip)

    if not nip.is_valid(nipId):  # 123-456-32-18
        raise HTTPException(status_code=400, detail="Invalid NIP number")

    db_user = session.execute(
        select(User)
        .where(User.service_token == res.token)
        .where(User.is_active == False)
        .where(User.service_token_valid_to > datetime.utcnow())
        .where(User.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    token = secrets.token_hex(64)

    db_account = session.execute(select(Account).where(Account.nip == nipId)).scalar_one_or_none()
    is_verified = False

    if not db_account:
        chars = "abcdefghijkmnopqrstuvwxyz23456789"
        company_ids = session.execute(select(Account.company_id)).all()
        proposed_id = "".join(random.choice(chars) for x in range(3))
        while proposed_id in company_ids:
            proposed_id = "".join(random.choice(chars) for x in range(3))
        # ----------------
        account_id = session.execute(select([func.max(User.account_id)])).scalar_one()
        if account_id is None:
            account_id = 0
        account_id += 2
        user_role_id = 1  # SUPER_ADMIN / USER / VIEWER
        is_verified = True

        # company_ids = session.exec(select(Accounts.company_id)).all()
        new_account = Account(
            uuid=str(uuid4()),
            company=f"Company_{account_id}",
            registered_at=datetime.utcnow(),
            nip=nipId,
            company_id=proposed_id,
            account_id=account_id,
        )
        session.add(new_account)
        session.commit()
        session.refresh(new_account)
    else:
        account_id = db_account.account_id
        user_role_id = 2  # SUPER_ADMIN / USER / VIEWER

    update_package = {
        "first_name": res.first_name,
        "last_name": res.last_name,
        "account_id": account_id,
        "is_active": True,
        "is_verified": is_verified,
        "user_role_id": user_role_id,
        "service_token": None,
        "service_token_valid_to": None,
        "auth_token": token,
        "auth_token_valid_to": datetime.utcnow() + timedelta(days=1),
        "updated_at": datetime.utcnow(),
    }

    #     # !TODO: Save NIP in customers table
    #     # url = "https://rejestr.io/api/v1/krs/28860"
    #     # payload={}
    #     # headers = {
    #     #   'Authorization': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    #     # }
    #     # response = requests.request("GET", url, headers=headers, data=payload)
    #     # print(response.text)

    for key, value in update_package.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    account = Account(uuid=str(uuid4()), account_id=db_user.account_id)
    session.add(account)
    session.commit()
    session.refresh(account)

    if user_role_id != 1:  # IF NOT ADMIN
        token = "abc"

    return {
        "ok": True,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "lang": db_user.lang,
        "tz": db_user.tz,
        "uuid": db_user.uuid,
        "token": token,
    }


@register_router.post("/login", response_model=UserLoginOut)  # , response_model=UserLoginOut
async def auth_login(*, session: Session = Depends(get_session), users: UserLoginIn, req: Request):
    # ip_info = "NO_INFO"  # get_ip_info(ip_addr)
    # ua_string = req.headers["User-Agent"]
    # user_agent = parse(ua_string)
    # browser_lang = req.headers["accept-language"]

    try:
        res = UserLoginIn.from_orm(users)

        db_user = session.execute(
            select(User).where(User.email == res.email).where(User.is_active == True).where(User.deleted_at.is_(None))
        ).scalar_one_or_none()

        print("#########", db_user.role_FK)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # if argon2.verify(res.password, db_user.password):
        #     token = secrets.token_hex(64)
        # else:
        #     raise HTTPException(status_code=401, detail="Incorrect username or password")

        # token_valid_to = datetime.utcnow() + timedelta(days=1)
        # if res.permanent is True:
        #     token_valid_to = datetime.utcnow() + timedelta(days=30)

        # update_package = {
        #     "auth_token": secrets.token_hex(64),  # token,
        #     "auth_token_valid_to": token_valid_to,
        #     "updated_at": datetime.utcnow(),
        # }

        # for key, value in update_package.items():
        #     setattr(db_user, key, value)
        # session.add(db_user)
        # session.commit()
        # session.refresh(db_user)

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

    return db_user


# @register_router.get("/verify/{token}", response_model=StandardResponse)
# async def auth_verify(*, session: Session = Depends(get_session), token: str):
#     user_db = session.exec(
#         select(Users)
#         .where(Users.auth_token == token)
#         .where(Users.is_active == True)
#         .where(Users.auth_token_valid_to > datetime.utcnow())
#         .where(Users.deleted_at.is_(None))
#     ).one_or_none()
#     if user_db is None:
#         raise HTTPException(status_code=404, detail="Invalid token")
#     return {"ok": True}


# @register_router.get("/remind-password/{user_email}", response_model=StandardResponse)
# async def auth_remind(*, session: Session = Depends(get_session), user_email: EmailStr, req: Request):
#     db_user = session.exec(
#         select(Users).where(Users.email == user_email).where(Users.is_active == True).where(Users.deleted_at.is_(None))
#     ).one_or_none()

#     if db_user is None:
#         return {"ok": True}
#         # raise HTTPException(status_code=404, detail="Invalid email")

#     token = secrets.token_hex(32)
#     update_package = {
#         "service_token": token,
#         "service_token_valid_to": datetime.utcnow() + timedelta(days=1),
#         "updated_at": datetime.utcnow(),
#     }

#     for key, value in update_package.items():
#         setattr(db_user, key, value)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)

#     # Notification
#     email = EmailNotification(settings.email_labs_app_key, settings.email_labs_secret_key, settings.email_smtp)

#     ua_string = req.headers["User-Agent"]
#     user_agent = parse(ua_string)

#     template_data = {  # Template: f91f8ad6 	ResetPassword_PL
#         "product_name": "Intio",
#         "name": db_user.first_name,
#         "action_url": "https://beta.remontmaszyn.pl/set_password/" + token,
#         "operating_system": user_agent.os.family,
#         "browser_name": user_agent.browser.family,
#     }

#     email.send(settings.email_sender, user_email, "[Intio] Resetowanie hasła!", "f91f8ad6", template_data)

#     return {"ok": True}


# @register_router.post("/set-password/", response_model=StandardResponse)
# async def auth_set_password(*, session: Session = Depends(get_session), user: UserSetPassIn):
#     res = UserSetPassIn.from_orm(user)

#     db_user = session.exec(
#         select(Users)
#         .where(Users.service_token == res.token)
#         .where(Users.is_active == True)
#         .where(Users.service_token_valid_to > datetime.utcnow())
#         .where(Users.deleted_at.is_(None))
#     ).one_or_none()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="Invalid email")

#     password = Password(res.password)
#     is_password_ok = password.compare(res.password_confirmation)

#     if is_password_ok is True:
#         pass_hash = argon2.hash(res.password)
#     else:
#         raise HTTPException(status_code=400, detail=is_password_ok)

#     update_package = {
#         "password": pass_hash,
#         "auth_token": None,
#         "service_token": None,
#         "service_token_valid_to": None,
#         "updated_at": datetime.utcnow(),
#     }

#     for key, value in update_package.items():
#         setattr(db_user, key, value)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)

#     return {"ok": True}
