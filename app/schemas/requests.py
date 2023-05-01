# from typing import list
from uuid import UUID

from pydantic import BaseModel, EmailStr
from pydantic.color import Color


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


class ResetPassword(BaseRequest):
    password: str


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
    symbol: str | None
    summary: str | None
    text_html: str | None
    text_json: dict | None
    files: list[UUID] | None


class ItemEditIn(BaseRequest):
    name: str | None
    symbol: str | None
    summary: str | None
    text_html: str | None
    text_json: dict | None
    files: list[UUID] | None


class GuideAddIn(BaseRequest):
    name: str
    text_html: str
    text_json: dict
    # video_id: str | None
    # video_json: dict | None
    files: list[UUID] | None
    item_uuid: str | None


class GuideEditIn(BaseRequest):
    name: str | None
    text_html: str | None
    text_json: dict | None
    # video_id: str | None
    # video_json: dict | None
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
    tags: list[UUID] | None


class FavouritesAddIn(BaseRequest):
    item_uuid: UUID | None
    user_uuid: UUID | None


class IssueEditIn(BaseRequest):
    name: str | None
    summary: str | None
    text_html: str | None
    text_json: dict | None
    files: list[UUID] | None
    tags: list[UUID] | None
    users: list[UUID] | None


class IssueChangeStatus(BaseRequest):
    status: str
    name: str | None
    title: str | None
    description: str | None
    internal_value: str | None


class SettingNotificationIn(BaseRequest):
    sms_notification_level: str | None
    email_notification_level: str | None


class SettingUserLanguage(BaseRequest):
    code: str


class SettingGeneralIn(BaseRequest):
    name: str
    value: str
    type: str


class TagCreateIn(BaseRequest):
    name: str
    color: str | None
    icon: str | None
    is_hidden: bool | None = False


class TagEditIn(BaseRequest):
    is_hidden: bool | None
    color: Color | None
