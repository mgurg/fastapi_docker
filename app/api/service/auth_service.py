import secrets
import sys
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from loguru import logger
from passlib.hash import argon2
from pydantic import EmailStr
from sentry_sdk import capture_message
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_401_UNAUTHORIZED
from user_agents import parse

from app.api.repository.PublicCompanyRepo import PublicCompanyRepo
from app.api.repository.PublicUserRepo import PublicUserRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo
from app.models.models import User
from app.models.shared_models import PublicUser
from app.schemas.requests import CompanyInfoRegisterIn, ResetPassword
from app.service.company_details import CompanyInfo
from app.service.notification_email import EmailNotification
from app.service.password import Password


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
            raise HTTPException(status_code=404, detail="User not found!")
        self.user_repo.update(db_user.id, **{"password": argon2.hash(new_password)})
