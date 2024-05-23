from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import EmailStr
from starlette.status import HTTP_204_NO_CONTENT

from app.api.service.auth_service import AuthService
from app.config import get_settings
from app.schemas.requests import CompanyInfoRegisterIn, ResetPassword, UserRegisterIn
from app.schemas.responses import (
    PublicCompanyCounterResponse,
    UserVerifyToken,
)

ACCOUNTS_LIMIT = 120

settings = get_settings()
auth_test_router = APIRouter()

AuthServiceDependency = Annotated[AuthService, Depends()]


@auth_test_router.get("/account_limit", response_model=PublicCompanyCounterResponse)
def auth_account_limit(auth_service: AuthServiceDependency):
    db_companies_quantity = auth_service.count_registered_accounts()
    return {"accounts": db_companies_quantity, "limit": ACCOUNTS_LIMIT}


@auth_test_router.post("/company_info")
async def auth_company_info(auth_service: AuthServiceDependency, company: CompanyInfoRegisterIn):
    company_details = auth_service.get_rich_registration_data(company)
    return company_details


@auth_test_router.post("/register", status_code=HTTP_204_NO_CONTENT)
def auth_register(auth_service: AuthServiceDependency, user_registration: UserRegisterIn):
    auth_service.register_new_company_account(user_registration)
    return None


@auth_test_router.get("/verify/{token}", response_model=UserVerifyToken)
def auth_verify(auth_service: AuthServiceDependency, token: str):
    return auth_service.verify_auth_token(token)


@auth_test_router.post("/logout/{token}", status_code=HTTP_204_NO_CONTENT)
def auth_login(auth_service: AuthServiceDependency, token: str):
    auth_service.logout(token)
    return None


@auth_test_router.get("/reset-password/{email}", status_code=HTTP_204_NO_CONTENT)
def auth_send_remind_password_to_email(auth_service: AuthServiceDependency, email: EmailStr, req: Request):
    auth_service.send_remind_password_to_email(email, req)
    return None


@auth_test_router.post("/reset-password/{token}", status_code=HTTP_204_NO_CONTENT)
def auth_reset_password_by_token(auth_service: AuthServiceDependency, token: str, reset_data: ResetPassword):
    auth_service.reset_password_by_token(token, reset_data)
    return None
