from typing import Annotated

from fastapi import Depends, HTTPException
from sentry_sdk import capture_message
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from app.api.repository.PublicCompanyRepo import PublicCompanyRepo
from app.api.repository.PublicUserRepo import PublicUserRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo
from app.models.models import User
from app.schemas.requests import CompanyInfoRegisterIn
from app.service.company_details import CompanyInfo


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
            capture_message("NIP not found: " + company.company_tax_id)
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail=f"Details for NIP {company.company_tax_id} not found"
            )

        return official_data

    def verify_auth_token(self, token: str) -> User | None:
        db_user = self.user_repo.get_user_by_auth_token(token)
        if db_user is None:
            raise HTTPException(status_code=401, detail="Invalid auth token")

        return db_user

    def logout(self, token: str) -> None:
        db_user = self.user_repo.get_user_by_auth_token(token)
        if db_user is None:
            raise HTTPException(status_code=401, detail="Invalid auth token")
        self.user_repo.update(db_user.id, **{"auth_token": None, "auth_token_valid_to": None})
