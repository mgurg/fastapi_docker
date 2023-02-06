import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from langcodes import standardize_tag
from loguru import logger
from passlib.hash import argon2
from sentry_sdk import capture_exception
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from unidecode import unidecode

from app.config import get_settings
from app.crud import crud_auth, crud_qr, crud_users
from app.db import engine, get_db, get_public_db
from app.models.models import User
from app.models.shared_models import PublicUser
from app.schemas.requests import CompanyInfoRegisterIn, UserFirstRunIn, UserLoginIn, UserRegisterIn
from app.schemas.responses import (
    ActivationResponse,
    CompanyInfoBasic,
    PublicCompanyCounterResponse,
    StandardResponse,
    UserLoginOut,
    UserQrToken,
    UserVerifyToken,
)
from app.service import auth
from app.service.company_details import CompanyDetails
from app.service.notification_email import EmailNotification
from app.service.password import Password
from app.service.scheduler import scheduler
from app.service.tenants import alembic_upgrade_head, tenant_create

settings = get_settings()
auth_router = APIRouter()


@auth_router.get("/account_limit", response_model=PublicCompanyCounterResponse)
def auth_account_limit(*, public_db: Session = Depends(get_public_db)):

    db_companies_no = crud_auth.get_public_company_count(public_db)
    limit = 20

    return {"accounts": db_companies_no, "limit": limit}


@auth_router.post("/company_info")
def auth_company_info(company: CompanyInfoRegisterIn):
    company_details = None
    try:
        company = CompanyDetails(country=company.country, tax_id=company.company_tax_id)
        company_details = company.get_company_details()  # VIES -> GUS -> Rejestr.io
    except Exception as e:
        print(e)
        capture_exception(e)

    if company_details is None:
        raise HTTPException(status_code=400, detail="Information not found")
    return company_details


@auth_router.post("/register", response_model=StandardResponse)
def auth_register(*, public_db: Session = Depends(get_public_db), user: UserRegisterIn):

    if auth.is_email_temporary(user.email):
        raise HTTPException(status_code=400, detail="Temporary email not allowed")

    db_user: PublicUser = crud_auth.get_public_user_by_email(public_db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    is_password_ok = Password(user.password).compare(user.password_confirmation)

    if is_password_ok is not True:
        raise HTTPException(status_code=400, detail=is_password_ok)

    if auth.is_timezone_correct is False:
        raise HTTPException(status_code=400, detail="Invalid timezone")

    db_company = crud_auth.get_public_company_by_nip(public_db, user.company_tax_id)

    if not db_company:
        uuid = str(uuid4())
        company = re.sub("[^A-Za-z0-9 _]", "", unidecode(user.company_name))
        tenant_id = "".join([company[:28], "_", uuid.replace("-", "")]).lower().replace(" ", "_")

        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            tenant_id = "fake_tenant_company_for_test_00000000000000000000000000000000"

        company_data = {
            "uuid": uuid,
            "name": user.company_name,
            "short_name": user.company_name,
            "nip": user.company_tax_id,
            "country": "pl",
            "city": user.company_city,
            "tenant_id": tenant_id,
            "qr_id": crud_qr.generate_company_qr_id(public_db),
            "created_at": datetime.now(timezone.utc),
        }

        db_company = crud_auth.create_public_company(public_db, company_data)

    else:
        tenant_id = db_company.tenant_id

    service_token = secrets.token_hex(32)
    if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
        today = datetime.now().strftime("%A-%Y-%m-%d-%H")
        service_token = ("a" * int(64 - len(today))) + today

    user = {
        "uuid": str(uuid4()),
        "email": user.email.strip(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "password": argon2.hash(user.password),
        "service_token": service_token,
        "service_token_valid_to": datetime.now(timezone.utc) + timedelta(days=1),
        "is_active": False,
        "is_verified": False,
        "tos": user.tos,
        "tenant_id": tenant_id,
        "tz": user.tz,
        "lang": standardize_tag(user.lang),
        "created_at": datetime.now(timezone.utc),
    }
    crud_auth.create_public_user(public_db, user)

    if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
        # tenant_create("fake_tenant_company_for_test_00000000000000000000000000000000")
        # alembic_upgrade_head("fake_tenant_company_for_test_00000000000000000000000000000000")
        logger.error("AUTH SCHEMA " + db_company.tenant_id)
        tenant_create(db_company.tenant_id)
        alembic_upgrade_head(db_company.tenant_id)
    else:
        scheduler.add_job(tenant_create, args=[db_company.tenant_id])
        scheduler.add_job(alembic_upgrade_head, args=[db_company.tenant_id])

    # Notification
    email = EmailNotification(settings.email_mailjet_app_key, settings.email_mailjet_secret_key)
    receiver = user["email"]

    template_data = {  # Template: 4b4653ba 	RegisterAdmin_PL
        "product_name": "Intio",
        "login_url": "https://beta.remontmaszyn.pl/login",
        "username": receiver,
        "sender_name": "Michał",
        "action_url": "https://beta.remontmaszyn.pl/activate/" + service_token,
    }
    email.send(receiver, "[Intio] Poprawmy coś razem!", "4b4653ba", template_data)

    return {"ok": True}


@auth_router.post("/first_run", response_model=ActivationResponse)
def auth_first_run(*, public_db: Session = Depends(get_public_db), user: UserFirstRunIn):
    """Activate user based on service token"""

    db_public_user: PublicUser = crud_auth.get_public_user_by_service_token(public_db, user.token)
    if not db_public_user:
        raise HTTPException(status_code=404, detail="User not found")

    connectable = engine.execution_options(schema_translate_map={"tenant": db_public_user.tenant_id})
    with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as db:

        db_user_cnt = crud_users.get_user_count(db)
        user_role_id = 2  # SUPER_ADMIN[1] / USER[2] / VIEWER[3]
        is_verified = False

        if db_user_cnt == 0:
            user_role_id = 1
            is_verified = True

        user_data = {
            "first_name": db_public_user.first_name,
            "last_name": db_public_user.last_name,
            "email": db_public_user.email,
            "password": db_public_user.password,
            "auth_token": secrets.token_hex(32),
            "auth_token_valid_to": datetime.now(timezone.utc) + timedelta(days=1),
            "role_id": user_role_id,
            "is_active": True,
            "is_verified": is_verified,
            "tos": db_public_user.tos,
            "lang": db_public_user.lang,
            "tz": db_public_user.tz,
            "tenant_id": db_public_user.tenant_id,
        }

        db_tenant_user = crud_auth.create_tenant_user(db, user_data)

    return {
        "ok": True,
        "first_name": db_tenant_user.first_name,
        "last_name": db_tenant_user.last_name,
        "lang": db_tenant_user.lang,
        "tz": db_tenant_user.tz,
        "uuid": db_tenant_user.uuid,
        "tenant_id": db_tenant_user.tenant_id,
        "token": db_tenant_user.auth_token,
    }


@auth_router.post("/login", response_model=UserLoginOut)
def auth_login(*, public_db: Session = Depends(get_public_db), user: UserLoginIn, req: Request):
    print(req.headers["User-Agent"])
    db_public_user: PublicUser = crud_auth.get_public_user_by_email(public_db, user.email)

    if db_public_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    schema_translate_map = dict(tenant=db_public_user.tenant_id)
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable) as db:

        db_user = crud_users.get_user_by_email(db, user.email)

        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if db_user.is_active is False:
            raise HTTPException(status_code=403, detail="User not activated")

        if db_user.is_verified is False:
            raise HTTPException(status_code=403, detail="User not verified yet")

        if argon2.verify(user.password, db_user.password) is False:
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        token_valid_to = datetime.now(timezone.utc) + timedelta(days=1)
        if user.permanent is True:
            token_valid_to = datetime.now(timezone.utc) + timedelta(days=30)

        update_package = {
            "auth_token": secrets.token_hex(64),  # token,
            "auth_token_valid_to": token_valid_to,
            "updated_at": datetime.now(timezone.utc),
        }

        crud_auth.update_tenant_user(db, db_user, update_package)

        # Load with relations
        db_user = db.execute(
            select(User).where(User.email == user.email).options(selectinload("*"))
        ).scalar_one_or_none()
        db_user.tenant_id = db_public_user.tenant_id

        return db_user


@auth_router.get("/company_summary", response_model=CompanyInfoBasic)
def get_company_summary(*, public_db: Session = Depends(get_public_db), request: Request):
    print(request.headers.get("tenant"))
    db_public_company = crud_auth.get_public_company_by_tenant_id(public_db, request.headers.get("tenant"))

    if db_public_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return db_public_company


# @auth_router.post("/login_tenant", response_model=UserLoginOut)
# def auth_login_tenant(*, db: Session = Depends(get_db), email: str, request: Request):

#     db_user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     db_user.tenant_id = request.headers["host"]
#     return db_user


@auth_router.get("/verify/{token}", response_model=UserVerifyToken)
def auth_verify(*, db: Session = Depends(get_db), token: str):
    user_db = crud_auth.get_tenant_user_by_auth_token(db, token)
    if user_db is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_user = db.execute(
        select(User).where(User.email == user_db.email).options(selectinload("*"))
    ).scalar_one_or_none()

    if db_user is None:
        raise HTTPException(status_code=401, detail="Strange error")

    return db_user


@auth_router.post("/qr/{qr_code}", response_model=UserQrToken)
def auth_verify_qr(*, public_db: Session = Depends(get_public_db), qr_code: str):

    pattern = re.compile(r"^[a-z2-9]{2,6}\+[a-z2-9]{2,3}$")
    if not pattern.match(qr_code):
        raise HTTPException(status_code=404, detail="Incorrect QR code")

    company, qr_id = qr_code.split("+")
    company = re.sub(r"\d+", "", company)

    db_company = crud_auth.get_public_company_by_qr_id(public_db, company)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found: " + company)

    token_valid_to = (datetime.now(timezone.utc) + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")

    base64_token = crud_auth.generate_base64_token(f"{db_company.tenant_id}.{token_valid_to}")

    connectable = engine.execution_options(schema_translate_map={"tenant": db_company.tenant_id})
    with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as db:
        db_qr = crud_qr.get_entity_by_qr_code(db, qr_id)
        if not db_qr:
            raise HTTPException(status_code=404, detail="QR not found")
        if db_qr.public_access is False:
            base64_token = None

        return {
            "resource": db_qr.resource,
            "resource_uuid": db_qr.resource_uuid,
            "url": f"/{db_qr.resource}/{db_qr.resource_uuid}",
            "anonymous_token": base64_token,
        }
