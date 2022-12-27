# from typing import list
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
    name: str
    summary: str | None
    text_json: dict
    text_html: str
    color: str = "green"
    files: list[UUID] | None


class IdeasVotesIn(BaseRequest):
    idea_uuid: UUID
    vote: str


class IdeaEditIn(BaseRequest):
    name: str | None
    summary: str | None
    text_json: dict | None
    text_html: str | None
    color: str | None
    status: str | None
    vote: str | None
    files: list[UUID] | None


class RoleAddIn(BaseRequest):
    title: str
    description: str
    permissions: list[UUID]


class RoleEditIn(BaseRequest):
    title: str | None
    description: str | None
    permissions: list[UUID] | None


class GroupAddIn(BaseRequest):
    name: str
    symbol: str | None
    description: str | None
    users: list[UUID] | None


class GroupEditIn(BaseRequest):
    name: str | None
    symbol: str | None
    description: str | None
    users: list[UUID] | None


class ItemAddIn(BaseRequest):
    name: str
    summary: str | None
    text_html: str | None
    text_json: dict | None
    files: list[UUID] | None


class ItemEditIn(BaseRequest):
    name: str | None
    summary: str | None
    text_html: str | None
    text_json: dict | None
    files: list[UUID] | None


class GuideAddIn(BaseRequest):
    name: str
    text_html: str
    text_json: dict
    video_id: str | None
    video_json: dict | None
    files: list[UUID] | None
    item_uuid: str | None


class GuideEditIn(BaseRequest):
    name: str | None
    text_html: str | None
    text_json: dict | None
    video_id: str | None
    video_json: dict | None
    files: list[UUID] | None


class IssueAddIn(BaseRequest):
    item_uuid: UUID | None
    name: str
    color: str | None
    priority: str | None
    status: str | None
    summary: str | None
    text_html: str | None
    text_json: dict | None
    files: list[UUID] | None


class IssueEditIn(BaseRequest):
    name: str | None
    summary: str | None
    text_html: str | None
    text_json: dict | None
    files: list[UUID] | None
