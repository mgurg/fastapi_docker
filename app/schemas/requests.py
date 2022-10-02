from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class CompanyInfoRegisterIn(BaseRequest):
    country: str | None = "pl"
    company_tax_id: str | None = "9542752600"


class UserRegisterIn(BaseRequest):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    password_confirmation: str
    country: str | None = "pl"
    company_tax_id: str | None = "9542752600"
    company_name: str
    company_street: str
    company_city: str
    company_postcode: str
    company_info_changed: bool
    tos: bool
    tz: str | None = "Europe/Warsaw"
    lang: str | None = "pl"


class UserFirstRunIn(BaseRequest):
    token: str


class UserLoginIn(BaseRequest):
    email: EmailStr
    password: str
    permanent: bool


class UserCreateIn(BaseRequest):
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    phone: str | None
    password: str | None
    password_confirmation: str | None
    is_verified: bool | None
    user_role_uuid: UUID | None


class IdeaAddIn(BaseRequest):
    title: str
    description: str
    body_json: dict
    body_html: str
    color: str = "green"
    files: List[UUID] | None


class IdeasVotesIn(BaseRequest):
    idea_uuid: UUID
    vote: str


class IdeaEditIn(BaseRequest):
    title: str | None
    description: str | None
    color: str | None
    status: str | None
    vote: str | None
    files: List[UUID] | None


class RoleAddIn(BaseRequest):
    title: str
    description: str
    permissions: List[UUID]


class RoleEditIn(BaseRequest):
    title: str | None
    description: str | None
    permissions: List[UUID] | None


class GroupAddIn(BaseRequest):
    name: str
    description: str | None
    users: list[UUID] | None


class GroupEditIn(BaseRequest):
    name: str | None
    description: str | None
    users: list[UUID] | None
