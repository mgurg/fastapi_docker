import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.crud import crud_auth, crud_qr, crud_users
from app.db import engine, get_db, get_public_db
from app.models.models import User
from app.models.shared_models import PublicUser
from app.schemas.requests import UserFirstRunIn, UserLoginIn
from app.schemas.responses import (
    ActivationResponse,
    UserLoginOut,
    UserQrToken,
)

settings = get_settings()
auth_router = APIRouter()

UserDB = Annotated[Session, Depends(get_db)]
PublicDB = Annotated[Session, Depends(get_public_db)]


# @auth_router.get("/account_limit", response_model=PublicCompanyCounterResponse)
# def auth_account_limit(*, public_db: PublicDB):
#     db_companies_no = crud_auth.get_public_company_count(public_db)
#     limit = 120
#
#     return {"accounts": db_companies_no, "limit": limit}
#
#
# @auth_router.post("/company_info")
# async def auth_company_info(*, public_db: PublicDB, company: CompanyInfoRegisterIn):
#     db_public_company = crud_auth.get_public_company_by_nip(public_db, company.company_tax_id)
#     if db_public_company:
#         raise HTTPException(status_code=400, detail="Company already registered")
#
#     company_details = None
#     try:
#         company = CompanyInfo(country=company.country, tax_id=company.company_tax_id)
#         company_details = company.get_details()  # VIES -> GUS -> Rejestr.io
#     except Exception as e:
#         print(e)
#         capture_exception(e)
#
#     if company_details is None:
#         capture_exception("NIP not found: " + company.company_tax_id)
#         raise HTTPException(status_code=404, detail="Information not found")
#
#     return company_details


# @auth_router.post("/register", response_model=StandardResponse)
# def auth_register(*, public_db: PublicDB, user: UserRegisterIn):
#     if auth_validators.is_email_temporary(user.email):
#         raise HTTPException(status_code=403, detail="Temporary email not allowed")
#
#     db_user: PublicUser = crud_auth.get_public_user_by_email(public_db, user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="User already exists")
#
#     is_password_ok = Password(user.password).compare(user.password_confirmation)
#
#     if is_password_ok is not True:
#         raise HTTPException(status_code=400, detail=is_password_ok)
#
#     if auth_validators.is_timezone_correct is False:
#         raise HTTPException(status_code=400, detail="Invalid timezone")
#
#     db_company = crud_auth.get_public_company_by_nip(public_db, user.company_tax_id)
#
#     if not db_company:
#         uuid = str(uuid4())
#         company = re.sub("[^A-Za-z0-9 _]", "", unidecode(user.company_name))
#         tenant_id = "".join([company[:28], "_", uuid.replace("-", "")]).lower().replace(" ", "_")
#
#         if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
#             tenant_id = "fake_tenant_company_for_test_00000000000000000000000000000000"
#
#         company_data = {
#             "uuid": uuid,
#             "name": user.company_name,
#             "short_name": user.company_name,
#             "nip": user.company_tax_id,
#             "country": "pl",
#             "city": user.company_city,
#             "tenant_id": tenant_id,
#             "qr_id": crud_qr.generate_company_qr_id(public_db),
#             "created_at": datetime.now(timezone.utc),
#         }
#
#         db_company = crud_auth.create_public_company(public_db, company_data)
#
#     else:
#         tenant_id = db_company.tenant_id
#
#     service_token = secrets.token_hex(32)
#     if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
#         today = datetime.now().strftime("%A-%Y-%m-%d-%H")
#         service_token = ("a" * int(64 - len(today))) + today
#
#     user = {
#         "uuid": str(uuid4()),
#         "email": user.email.strip(),
#         "first_name": user.first_name,
#         "last_name": user.last_name,
#         "password": argon2.hash(user.password),
#         "service_token": service_token,
#         "service_token_valid_to": datetime.now(timezone.utc) + timedelta(days=1),
#         "is_active": False,
#         "is_verified": False,
#         "tos": user.tos,
#         "tenant_id": tenant_id,
#         "tz": user.tz,
#         "lang": standardize_tag(user.lang),
#         "created_at": datetime.now(timezone.utc),
#     }
#     new_db_user = crud_auth.create_public_user(public_db, user)
#
#     if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
#         # tenant_create("fake_tenant_company_for_test_00000000000000000000000000000000")
#         # alembic_upgrade_head("fake_tenant_company_for_test_00000000000000000000000000000000")
#         logger.error("AUTH SCHEMA " + db_company.tenant_id)
#         create_new_db_schema(db_company.tenant_id)
#         alembic_upgrade_head(db_company.tenant_id)
#     else:
#         scheduler.add_job(create_new_db_schema, args=[db_company.tenant_id])
#         scheduler.add_job(alembic_upgrade_head, args=[db_company.tenant_id])
#
#     if user["email"].split("@")[1] == "example.com":
#         return {"ok": True}
#
#     # Notification
#     email = EmailNotification()
#     email.send_admin_registration(new_db_user, f"/activate/{service_token}")
#
#     return {"ok": True}


@auth_router.post("/first_run", response_model=ActivationResponse)
def auth_first_run(*, public_db: PublicDB, user: UserFirstRunIn):
    """Activate user based on service token"""

    db_public_user: PublicUser = crud_auth.get_public_user_by_service_token(public_db, user.token)
    if not db_public_user:
        raise HTTPException(status_code=404, detail="User not found")

    connectable = engine.execution_options(schema_translate_map={"tenant": db_public_user.tenant_id})
    with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as db:
        db_user_cnt = crud_users.get_user_count(db)
        user_role_id = 2  # ADMIN_MASTER[1] / ADMIN[2]
        is_verified = False

        if db_user_cnt == 0:
            user_role_id = 1
            is_verified = True

        user_data = {
            "uuid": db_public_user.uuid,
            "first_name": db_public_user.first_name,
            "last_name": db_public_user.last_name,
            "email": db_public_user.email,
            "password": db_public_user.password,
            "auth_token": secrets.token_hex(32),
            "auth_token_valid_to": datetime.now(timezone.utc) + timedelta(days=1),
            "user_role_id": user_role_id,
            "is_active": True,
            "is_verified": is_verified,
            "is_visible": True,
            "tos": db_public_user.tos,
            "lang": db_public_user.lang,
            "tz": db_public_user.tz,
            "tenant_id": db_public_user.tenant_id,
            "created_at": datetime.now(timezone.utc),
        }

        anonymous_user_data = {
            "uuid": str(uuid4()),
            "first_name": "Anonymous",
            "last_name": "User",
            "email": "anonymous@example.com",
            "password": None,
            "auth_token": secrets.token_hex(32),
            "auth_token_valid_to": datetime.now(timezone.utc) + timedelta(days=1),
            "user_role_id": None,
            "is_active": True,
            "is_verified": True,
            "is_visible": False,
            "tos": True,
            "lang": "pl",
            "tz": "Europe/Warsaw",
            "tenant_id": db_public_user.tenant_id,
            "created_at": datetime.now(timezone.utc),
        }

        crud_auth.create_tenant_user(db, anonymous_user_data)
        db_tenant_user = crud_auth.create_tenant_user(db, user_data)

    empty_data = {
        "service_token": None,
        "service_token_valid_to": None,
        "password": None,
        "is_active": True,
        "is_verified": True,
    }
    crud_auth.update_public_user(public_db, db_public_user, empty_data)

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
def auth_login(*, public_db: PublicDB, user: UserLoginIn, req: Request):
    print(req.headers["User-Agent"])
    db_public_user: PublicUser = crud_auth.get_public_user_by_email(public_db, user.email)

    if db_public_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    schema_translate_map = {"tenant": db_public_user.tenant_id}
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

        crud_users.update_user(db, db_user, update_package)

        # Load with relations
        query = select(User).where(User.email == user.email).options(selectinload("*"))
        db_user = db.execute(query).scalar_one_or_none()
        db_user.tenant_id = db_public_user.tenant_id

        return db_user


# @auth_router.get("/company_summary", response_model=CompanyInfoBasic)
# def get_company_summary(*, public_db: PublicDB, request: Request):
#     print(request.headers.get("tenant"))
#     db_public_company = crud_auth.get_public_company_by_tenant_id(public_db, request.headers.get("tenant"))
#
#     if db_public_company is None:
#         raise HTTPException(status_code=404, detail="Company not found")
#
#     return db_public_company


# @auth_router.post("/login_tenant", response_model=UserLoginOut)
# def auth_login_tenant(*, db: Session = Depends(get_db), email: str, request: Request):

#     db_user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     db_user.tenant_id = request.headers["host"]
#     return db_user


# @auth_router.get("/verify/{token}", response_model=UserVerifyToken)
# def auth_verify(*, db: UserDB, token: str):
#     user_db = crud_auth.get_tenant_user_by_auth_token(db, token)
#     if user_db is None:
#         raise HTTPException(status_code=401, detail="Invalid token")
#
#     db_user = db.execute(
#         select(User).where(User.email == user_db.email).options(selectinload("*"))
#     ).scalar_one_or_none()
#
#     if db_user is None:
#         raise HTTPException(status_code=401, detail="Strange error")
#
#     return db_user


# @auth_router.get("/reset-password/{email}", response_model=StandardResponse)
# def auth_remind_password(*, public_db: PublicDB, email: EmailStr, req: Request):
#     user_agent = parse(req.headers["User-Agent"])
#     ua_os = user_agent.os.family
#     ua_browser = user_agent.browser.family
#
#     db_public_user: PublicUser = crud_auth.get_public_user_by_email(public_db, email)
#
#     if db_public_user is None:
#         logger.warning(f"reset password for nonexisting email {email} , OS: {ua_os}, browser: {ua_browser}")
#         return {"ok": True}
#         # raise HTTPException(status_code=404, detail="User not found")
#
#     service_token = secrets.token_hex(32)
#
#     update_user = {
#         "service_token": service_token,
#         "service_token_valid_to": datetime.now(timezone.utc) + timedelta(days=1),
#         "updated_at": datetime.now(timezone.utc),
#     }
#
#     crud_auth.update_public_user(public_db, db_public_user, update_user)
#
#     email_notification = EmailNotification()
#     email_notification.send_password_reset_request(db_public_user, service_token, ua_browser, ua_os)
#
#     return {"ok": True}


# @auth_router.post("/reset-password/{token}", response_model=StandardResponse)
# def auth_reset_password(*, public_db: PublicDB, token: str, reset_data: ResetPassword):
#     is_password_ok = Password(reset_data.password).compare(reset_data.password)
#
#     if is_password_ok is not True:
#         raise HTTPException(status_code=400, detail=is_password_ok)
#
#     db_public_user: PublicUser = crud_auth.get_public_active_user_by_service_token(public_db, token)
#
#     if db_public_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     connectable = engine.execution_options(schema_translate_map={"tenant": db_public_user.tenant_id})
#     with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as db:
#         db_user = crud_users.get_user_by_uuid(db, db_public_user.uuid)
#         if db_user is None:
#             raise HTTPException(status_code=404, detail="User not found!")
#         update_package = {"password": argon2.hash(reset_data.password)}
#         crud_users.update_user(db, db_user, update_package)
#
#     crud_auth.update_public_user(public_db, db_public_user, {"service_token": None, "service_token_valid_to": None})
#
#     return {"ok": True}


@auth_router.post("/qr/{qr_code}", response_model=UserQrToken)
def auth_verify_qr(*, public_db: PublicDB, qr_code: str):
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
