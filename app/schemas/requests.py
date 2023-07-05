# from typing import list
from uuid import UUID

from pydantic import BaseModel, EmailStr, condecimal
from pydantic_extra_types.color import Color


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
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    password: str | None = None
    password_confirmation: str | None = None
    is_verified: bool | None = None
    user_role_uuid: UUID | None = None


class IdeaAddIn(BaseRequest):
    name: str
    summary: str | None = None
    text_json: dict
    text_html: str
    color: str = "green"
    files: list[UUID] | None = None


class IdeasVotesIn(BaseRequest):
    idea_uuid: UUID
    vote: str


class IdeaEditIn(BaseRequest):
    name: str | None = None
    summary: str | None = None
    text_json: dict | None = None
    text_html: str | None = None
    color: str | None = None
    status: str | None = None
    vote: str | None = None
    files: list[UUID] | None = None


class RoleAddIn(BaseRequest):
    title: str
    description: str | None = None
    permissions: list[UUID]


class RoleEditIn(BaseRequest):
    title: str | None = None
    description: str | None = None
    permissions: list[UUID] | None = None


class GroupAddIn(BaseRequest):
    name: str
    symbol: str | None = None
    description: str | None = None
    users: list[UUID] | None = None


class GroupEditIn(BaseRequest):
    name: str | None = None
    symbol: str | None = None
    description: str | None = None
    users: list[UUID] | None = None


class ItemAddIn(BaseRequest):
    name: str
    symbol: str | None = None
    summary: str | None = None
    text_html: str | None = None
    text_json: dict | None = None
    files: list[UUID] | None = None


class ItemEditIn(BaseRequest):
    name: str | None = None
    symbol: str | None = None
    summary: str | None = None
    text_html: str | None = None
    text_json: dict | None = None
    files: list[UUID] | None = None


class GuideAddIn(BaseRequest):
    name: str
    text_html: str
    text_json: dict
    # video_id: str | None
    # video_json: dict | None
    files: list[UUID] | None = None
    item_uuid: UUID | None = None


class GuideEditIn(BaseRequest):
    name: str | None = None
    text_html: str | None = None
    text_json: dict | None = None
    # video_id: str | None
    # video_json: dict | None
    files: list[UUID] | None = None


class IssueAddIn(BaseRequest):
    item_uuid: UUID | None = None
    name: str
    color: str | None = None
    priority: str | None = None
    status: str | None = None
    summary: str | None = None
    text_html: str | None = None
    text_json: dict | None = None
    files: list[UUID] | None = None
    tags: list[UUID] | None = None


class FavouritesAddIn(BaseRequest):
    item_uuid: UUID | None = None
    user_uuid: UUID | None = None


class IssueEditIn(BaseRequest):
    name: str | None = None
    priority: str | None = None
    summary: str | None = None
    text_html: str | None = None
    text_json: dict | None = None
    files: list[UUID] | None = None
    tags: list[UUID] | None = None
    users: list[UUID] | None = None


class IssueChangeStatus(BaseRequest):
    status: str
    name: str | None = None
    title: str | None = None
    description: str | None = None
    internal_value: str | None = None


class SettingNotificationIn(BaseRequest):
    sms_notification_level: str | None = None
    email_notification_level: str | None = None


class SettingUserLanguage(BaseRequest):
    code: str


class SettingGeneralIn(BaseRequest):
    name: str
    value: str
    type: str


class TagCreateIn(BaseRequest):
    name: str
    color: str | None = None
    icon: str | None = None
    is_hidden: bool | None = False


class TagEditIn(BaseRequest):
    is_hidden: bool | None = None
    color: Color | None = None


class PartCreateIn(BaseRequest):
    issue_uuid: UUID
    name: str
    description: str | None = None
    price: condecimal(max_digits=10, decimal_places=2)
    quantity: condecimal(max_digits=4, decimal_places=2)
    unit: str | None = None
    value: condecimal(max_digits=10, decimal_places=2) | None = None


class PartEditIn(BaseRequest):
    name: str | None = None
    description: str | None = None
    price: condecimal(max_digits=10, decimal_places=2) | None = None
    quantity: condecimal(max_digits=4, decimal_places=2) | None = None
    unit: str | None = None
    value: condecimal(max_digits=10, decimal_places=2) | None = None
