from typing import Annotated

from fastapi import APIRouter, Depends, Header
from pydantic import EmailStr
from starlette.status import HTTP_204_NO_CONTENT

from app.api.service.auth_service import AuthService
from app.config import get_settings
from app.schemas.requests import CompanyInfoRegisterIn, ResetPassword, UserFirstRunIn, UserLoginIn, UserRegisterIn
from app.schemas.responses import (
    ActivationResponse,
    CompanyInfoBasic,
    PublicCompanyCounterResponse,
    TenantUidOut,
    UserLoginOut,
    UserQrToken,
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


@auth_test_router.get("/company_summary", response_model=CompanyInfoBasic)
def get_company_summary(auth_service: AuthServiceDependency, tenant: Annotated[str | None, Header()] = None):
    # TODO: verify if needed
    company_summary = auth_service.get_company_summary(tenant)
    return company_summary


@auth_test_router.post("/register", status_code=HTTP_204_NO_CONTENT)
def auth_register(auth_service: AuthServiceDependency, user_registration: UserRegisterIn):
    auth_service.register_new_company_account(user_registration)
    return None


@auth_test_router.get("/get_tenant_uid", response_model=TenantUidOut)
def auth_get_tenant_uid(auth_service: AuthServiceDependency, email: EmailStr):
    tenant_uid = auth_service.get_tenant_uid(email)
    return {"tenant_uid": tenant_uid}


@auth_test_router.post("/first_run", response_model=ActivationResponse)
def auth_first_run(auth_service: AuthServiceDependency, user: UserFirstRunIn):
    return auth_service.first_run_activation(user)


@auth_test_router.post("/login", response_model=UserLoginOut)
def auth_login(
    auth_service: AuthServiceDependency,
    login_data: UserLoginIn,
    user_agent: Annotated[str | None, Header()] = None,
):
    auth_service.login(login_data, user_agent)


@auth_test_router.get("/verify/{token}", response_model=UserVerifyToken)
def auth_verify(auth_service: AuthServiceDependency, token: str):
    return auth_service.verify_auth_token(token)


@auth_test_router.post("/logout/{token}", status_code=HTTP_204_NO_CONTENT)
def auth_logout(auth_service: AuthServiceDependency, token: str):
    auth_service.logout(token)
    return None


@auth_test_router.get("/reset-password/{email}", status_code=HTTP_204_NO_CONTENT)
def auth_send_remind_password_to_email(
    auth_service: AuthServiceDependency, email: EmailStr, user_agent: Annotated[str | None, Header()] = None
):
    auth_service.send_remind_password_to_email(email, user_agent)
    return None


@auth_test_router.post("/reset-password/{token}", status_code=HTTP_204_NO_CONTENT)
def auth_reset_password_by_token(auth_service: AuthServiceDependency, token: str, reset_data: ResetPassword):
    auth_service.reset_password_by_token(token, reset_data)
    return None


@auth_test_router.post("/qr/{qr_code}", response_model=UserQrToken)
def auth_verify_qr(auth_service: AuthServiceDependency, qr_code: str):
    auth_service.get_temporary_creditentials_for_qrcode()
    return None
