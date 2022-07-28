import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.crud import crud_auth, crud_users
from app.db import engine, get_db, get_public_db
from app.models.models import User
from app.models.shared_models import PublicUser
from app.schemas.requests import UserFirstRunIn, UserLoginIn, UserRegisterIn
from app.schemas.responses import StandardResponse  # UserLoginOut
from app.schemas.schemas import UserLoginOut
from app.service import auth
from app.service.api_rejestr_io import get_company_details
from app.service.password import Password
from app.service.tenants import alembic_upgrade_head, tenant_create

auth_router = APIRouter()


@auth_router.post("/register", response_model=StandardResponse)
async def auth_register(*, shared_db: Session = Depends(get_public_db), user: UserRegisterIn):

    if auth.is_email_temporary(user.email):
        raise HTTPException(status_code=400, detail="Temporary email not allowed")

    db_user: PublicUser = crud_auth.get_public_user_by_email(shared_db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    is_password_ok = Password(user.password).compare(user.password_confirmation)

    if is_password_ok is not True:
        raise HTTPException(status_code=400, detail=is_password_ok)

    if auth.is_timezone_correct is False:
        raise HTTPException(status_code=400, detail="Invalid timezone")

    crud_auth.create_public_user(shared_db, user)

    return {"ok": True}


@auth_router.post("/first_run")
async def auth_first_run(*, shared_db: Session = Depends(get_public_db), user: UserFirstRunIn):
    """Activate user based on service token"""

    if auth.is_nip_correct(user.nip):  # 123-456-32-18 - CompanyID number
        raise HTTPException(status_code=400, detail="Invalid NIP number")

    db_user: PublicUser = crud_auth.get_public_user_by_service_token(shared_db, user.token)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_company = crud_auth.get_public_company_by_nip(shared_db, user.nip)
    user_role_id = 2  # SUPER_ADMIN[1] / USER[2] / VIEWER[3]
    is_verified = False

    if not db_company:
        company_data = get_company_details(user.nip)

        db_company = crud_auth.create_public_company(shared_db, company_data)

        tenant_create(db_company.tenant_id)
        alembic_upgrade_head(db_company.tenant_id)
        user_role_id = 1  # SUPER_ADMIN[1] / USER[2] / VIEWER[3]
        is_verified = True

    update_db_user = {
        "tenant_id": db_company.tenant_id,
        # "is_active": True,
        # "is_verified": is_verified,
        # "user_role_id": user_role_id,
        # "service_token": None,
        # "service_token_valid_to": None,
        "updated_at": datetime.utcnow(),
    }

    crud_auth.update_public_user(shared_db, db_user, update_db_user)
    connectable = engine.execution_options(schema_translate_map={"tenant": db_company.tenant_id})
    with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as db:

        tenant_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": db_user.email,
            "password": db_user.password,
            "auth_token": secrets.token_hex(32),
            "auth_token_valid_to": datetime.utcnow() + timedelta(days=1),
            "role_id": user_role_id,
            "is_active": True,
            "is_verified": is_verified,
            "tos": db_user.tos,
            "lang": db_user.lang,
            "tz": db_user.tz,
            "tenant_id": db_company.tenant_id,
        }

        db_tennat_user = crud_auth.create_tenant_user(db, tenant_data)

    return {
        "ok": True,
        "first_name": db_tennat_user.first_name,
        "last_name": db_tennat_user.last_name,
        "lang": db_tennat_user.lang,
        "tz": db_tennat_user.tz,
        "uuid": db_tennat_user.uuid,
        "tenanat_id": db_tennat_user.tenant_id,
        "token": db_tennat_user.auth_token,
    }


@auth_router.post("/login", response_model=UserLoginOut)
async def auth_login(*, shared_db: Session = Depends(get_public_db), user: UserLoginIn, req: Request):
    req.headers["User-Agent"]
    db_public_user: PublicUser = crud_auth.get_public_user_by_email(shared_db, user.email)

    if db_public_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    schema_translate_map = dict(tenant=db_public_user.tenant_id)
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable) as db:

        db_user = crud_users.get_user_by_email(db, user.email)

        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if argon2.verify(user.password, db_user.password) is False:
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        token_valid_to = datetime.utcnow() + timedelta(days=1)
        if user.permanent is True:
            token_valid_to = datetime.utcnow() + timedelta(days=30)

        update_package = {
            "auth_token": secrets.token_hex(64),  # token,
            "auth_token_valid_to": token_valid_to,
            "updated_at": datetime.utcnow(),
        }

        db_user = crud_auth.update_tenant_user(db, db_user, update_package)

        # Load with relations
        db_user = db.execute(
            select(User).where(User.email == user.email).options(selectinload("*"))
        ).scalar_one_or_none()
        db_user.tenant_id = db_public_user.tenant_id

        return db_user


@auth_router.post("/login_tenant", response_model=UserLoginOut)
async def auth_login(*, db: Session = Depends(get_db), email: str, request: Request):

    db_user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.tenant_id = request.headers["host"]
    return db_user


@auth_router.get("/verify/{token}", response_model=StandardResponse)
async def auth_verify(*, db: Session = Depends(get_db), token: str):
    user_db = crud_auth.get_tenant_user_by_auth_token(db, token)
    if user_db is None:
        raise HTTPException(status_code=403, detail="Invalid token")
    return {"ok": True}
