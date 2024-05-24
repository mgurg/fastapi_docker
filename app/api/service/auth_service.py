import os
import re
import secrets
import sys
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, Request
from langcodes import standardize_tag
from loguru import logger
from passlib.hash import argon2
from pydantic import EmailStr
from sentry_sdk import capture_message
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)
from unidecode import unidecode
from user_agents import parse

from app.api.repository.PublicCompanyRepo import PublicCompanyRepo
from app.api.repository.PublicUserRepo import PublicUserRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo
from app.models.models import User
from app.models.shared_models import PublicCompany, PublicUser
from app.schemas.requests import CompanyInfoRegisterIn, ResetPassword, UserFirstRunIn, UserLoginIn, UserRegisterIn
from app.service import auth_validators
from app.service.company_details import CompanyInfo
from app.service.notification_email import EmailNotification
from app.service.password import Password
from app.service.scheduler import scheduler
from app.service.tenants import alembic_upgrade_head, create_new_db_schema

TEST_TENANT_ID = "fake_tenant_company_for_test_123456789000000000000000000000000"


class AuthService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends()],
        role_repo: Annotated[RoleRepo, Depends()],
        public_user_repo: Annotated[PublicUserRepo, Depends()],
        public_company_repo: Annotated[PublicCompanyRepo, Depends()],
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.public_user_repo = public_user_repo
        self.public_company_repo = public_company_repo

    def count_registered_accounts(self) -> int | None:
        return self.public_company_repo.get_users_count()

    def get_public_user_by_service_token(self, service_token: str) -> PublicUser:
        db_public_user = self.public_user_repo.get_by_service_token(service_token)
        if not db_public_user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
        return db_public_user

    def finalize_first_run(self) -> None: ...

    def get_rich_registration_data(self, company: CompanyInfoRegisterIn) -> dict:
        db_public_company = self.public_company_repo.get_by_nip(company.company_tax_id)
        if db_public_company:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT, detail=f"NIP {company.company_tax_id} already registered"
            )

        # VIES -> GUS -> Rejestr.io
        official_data = CompanyInfo(country=company.country, tax_id=company.company_tax_id).get_details()

        if official_data is None:
            capture_message(f"NIP not found: {company.company_tax_id}")
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail=f"Details for NIP {company.company_tax_id} not found"
            )

        return official_data

    def get_company_summary(self, tenant_header: str):
        db_public_company = self.public_company_repo.get_by_tenant_uid(tenant_header)

        if db_public_company is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Company not found")

        return db_public_company

    def register_new_company_account(self, user_registration: UserRegisterIn):
        if auth_validators.is_email_temporary(user_registration.email):
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Temporary email not allowed")

        is_password_ok = Password(user_registration.password).compare(user_registration.password_confirmation)

        if is_password_ok is not True:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=is_password_ok)

        if auth_validators.is_timezone_correct is False:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid timezone")

        db_public_user = self.public_user_repo.get_by_email(user_registration.email)
        if db_public_user:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"User {user_registration.email} exists")

        is_new_company = False
        db_public_company = self.public_company_repo.get_by_nip(user_registration.company_tax_id)
        if not db_public_company:
            db_public_company = self.register_new_public_company(user_registration)
            is_new_company = True

        tenant_id = db_public_company.id

        new_db_public_user = self.register_new_public_user(tenant_id, user_registration)

        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            logger.error("TEST AUTH SCHEMA " + db_public_company.tenant_id)
            create_new_db_schema(db_public_company.tenant_id)
            alembic_upgrade_head(db_public_company.tenant_id)
            return True

        if is_new_company:
            scheduler.add_job(create_new_db_schema, args=[db_public_company.tenant_id])
            scheduler.add_job(alembic_upgrade_head, args=[db_public_company.tenant_id])

        if user_registration.email.split("@")[1] == "example.com":
            return True

        # Notification
        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            email = EmailNotification()
            email.send_admin_registration(new_db_public_user, f"/activate/{new_db_public_user.service_token}")

        return True

    def register_new_public_user(self, tenant_id, user_registration) -> PublicUser:
        service_token = secrets.token_hex(32)
        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            today = datetime.now().strftime("%A-%Y-%m-%d-%H")
            service_token = ("a" * int(64 - len(today))) + today

        user = {
            "uuid": str(uuid4()),
            "email": user_registration.email.strip(),
            "first_name": user_registration.first_name,
            "last_name": user_registration.last_name,
            "password": argon2.hash(user_registration.password),
            "service_token": service_token,
            "service_token_valid_to": datetime.now(timezone.utc) + timedelta(days=1),
            "is_active": False,
            "is_verified": False,
            "tos": user_registration.tos,
            "tenant_id": tenant_id,
            "tz": user_registration.tz,
            "lang": standardize_tag(user_registration.lang),
            "created_at": datetime.now(timezone.utc),
        }
        new_db_user = self.public_user_repo.create(**user)
        return new_db_user

    def register_new_public_company(self, user_registration) -> PublicCompany:
        db_public_company_uuid = str(uuid4())
        company = re.sub("[^A-Za-z0-9 _]", "", unidecode(user_registration.company_name))
        tenant_id = "".join([company[:28], "_", db_public_company_uuid.replace("-", "")]).lower().replace(" ", "_")
        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            tenant_id = TEST_TENANT_ID
        company_data = {
            "uuid": db_public_company_uuid,
            "name": user_registration.company_name,
            "short_name": user_registration.company_name,
            "nip": user_registration.company_tax_id,
            "country": "pl",
            "city": user_registration.company_city,
            "tenant_id": tenant_id,
            "qr_id": "afxp",  # TODO crud_qr.generate_company_qr_id(public_db),
            "created_at": datetime.now(timezone.utc),
        }
        new_db_company = self.public_company_repo.create(**company_data)
        return new_db_company

    def get_tenant_uid(self, email: EmailStr):
        db_public_user = self.public_user_repo.get_by_email(email)
        if db_public_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return db_public_user.tenant_id

    def first_run_activation(self, user: UserFirstRunIn):
        db_public_user = self.get_public_user_by_service_token(user.token)

        db_user_cnt = self.user_repo.get_users_count()
        user_role_id = 2  # ADMIN_MASTER[1] / ADMIN[2]
        is_verified = False

        if db_user_cnt == 0:
            user_role_id = 1
            is_verified = True

        common_data = {
            "is_active": True,
            "tenant_id": db_public_user.tenant_id,
            "created_at": datetime.now(timezone.utc),
        }

        user_data = {
            "uuid": db_public_user.uuid,
            "first_name": db_public_user.first_name,
            "last_name": db_public_user.last_name,
            "email": db_public_user.email,
            "password": db_public_user.password,
            "auth_token": secrets.token_hex(32),
            "auth_token_valid_to": datetime.now(timezone.utc) + timedelta(days=1),
            "user_role_id": user_role_id,
            # "is_active": True,
            "is_verified": is_verified,
            "is_visible": True,
            "tos": db_public_user.tos,
            "lang": db_public_user.lang,
            "tz": db_public_user.tz,
            **common_data,
            # "tenant_id": db_public_user.tenant_id,
            # "created_at": datetime.now(timezone.utc),
        }

        anonymous_user_data = {
            "uuid": str(uuid4()),
            "first_name": "Anonymous",
            "last_name": "User",
            "email": "anonymous@example.com",
            "password": None,
            "auth_token": secrets.token_hex(32),
            "auth_token_valid_to": datetime.now(timezone.utc),
            "user_role_id": None,
            # "is_active": True,
            "is_verified": True,
            "is_visible": False,
            "tos": True,
            "lang": "pl",
            "tz": "Europe/Warsaw",
            **common_data,
            # "tenant_id": db_public_user.tenant_id,
            # "created_at": datetime.now(timezone.utc),
        }

        _db_new_anonymous_user = self.user_repo.create(**anonymous_user_data)
        db_new_master_admin_user = self.user_repo.create(**user_data)

        empty_data = {
            "service_token": None,
            "service_token_valid_to": None,
            "password": None,
            "is_active": True,
            "is_verified": True,
        }

        # TODO: clean
        # crud_auth.update_public_user(public_db, db_public_user, empty_data)

        return {
            "ok": True,
            "first_name": db_new_master_admin_user.first_name,
            "last_name": db_new_master_admin_user.last_name,
            "lang": db_new_master_admin_user.lang,
            "tz": db_new_master_admin_user.tz,
            "uuid": db_new_master_admin_user.uuid,
            "tenant_id": db_new_master_admin_user.tenant_id,
            "token": db_new_master_admin_user.auth_token,
        }

    def login(self, login_data: UserLoginIn, user_agent: str):
        db_user = self.user_repo.get_by_email(login_data.email)

        if db_user is None or argon2.verify(login_data.password, db_user.password) is False:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        if db_user.is_active is False:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=f"User {login_data.email} not activated")

        if db_user.is_verified is False:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=f"User {login_data.email} not verified yet")

        days_to_add: int = 30 if login_data.permanent else 1
        token_valid_to = datetime.now(timezone.utc) + timedelta(days=days_to_add)

        new_auth_token = secrets.token_hex(64)
        update_package = {
            "auth_token": new_auth_token,  # token,
            "auth_token_valid_to": token_valid_to,
            "updated_at": datetime.now(timezone.utc),
        }
        self.user_repo.update(db_user.id, **update_package)

        updated_db_user = self.user_repo.get_user_by_auth_token(new_auth_token)

        return updated_db_user

    def verify_auth_token(self, token: str) -> User | None:
        db_user = self.user_repo.get_user_by_auth_token(token)
        if db_user is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid auth token")

        return db_user

    def logout(self, token: str) -> None:
        db_user = self.user_repo.get_user_by_auth_token(token)
        if db_user is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid auth token")
        self.user_repo.update(db_user.id, **{"auth_token": None, "auth_token_valid_to": None})

    def send_remind_password_to_email(self, email: EmailStr, req: Request) -> None:
        user_agent = parse(req.headers["User-Agent"])
        os = user_agent.os.family
        browser = user_agent.browser.family

        db_public_user = self.public_user_repo.get_by_email(email)

        if db_public_user is None:
            logger.warning(f"Reset password for nonexistent email `{email}` , OS: `{os}`, browser: `{browser}`")
            return None

        service_token = secrets.token_hex(32)

        update_user = {
            "service_token": service_token,
            "service_token_valid_to": datetime.now(timezone.utc) + timedelta(days=1),
            "updated_at": datetime.now(timezone.utc),
        }

        self.public_user_repo.update(db_public_user.id, **update_user)

        email_notification = EmailNotification()
        email_notification.send_password_reset_request(db_public_user, service_token, browser, os)

        return None

    def reset_password_by_token(self, token: str, reset_data: ResetPassword) -> None:
        is_password_ok = Password(reset_data.password).compare(reset_data.password)

        if is_password_ok is not True:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=is_password_ok)

        db_public_user: PublicUser = self.public_user_repo.get_by_service_token(token)

        if db_public_user is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

        if "pytest" not in sys.modules:
            self.update_user_password(db_public_user.uuid, reset_data.password)

        self.public_user_repo.update(db_public_user.id, **{"service_token": None, "service_token_valid_to": None})

        return None

    def update_user_password(self, user_uuid: UUID, new_password: str):
        db_user = self.user_repo.get_by_uuid(user_uuid)
        if db_user is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found!")
        self.user_repo.update(db_user.id, **{"password": argon2.hash(new_password)})
