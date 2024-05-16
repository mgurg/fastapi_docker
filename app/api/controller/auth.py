from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.service.auth_service import AuthService
from app.config import get_settings
from app.schemas.responses import (
    PublicCompanyCounterResponse,
)

ACCOUNTS_LIMIT = 120

settings = get_settings()
auth_test_router = APIRouter()

AuthServiceDependency = Annotated[AuthService, Depends()]


@auth_test_router.get("/account_limit", response_model=PublicCompanyCounterResponse)
def auth_account_limit(auth_service: AuthServiceDependency):
    db_companies_no = auth_service.get_limit()
    return {"accounts": db_companies_no, "limit": ACCOUNTS_LIMIT}
