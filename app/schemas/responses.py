from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseResponse(BaseModel):
    # may define additional fields or config shared across responses
    class Config:
        orm_mode = True


class StandardResponse(BaseResponse):
    ok: bool


class ActivationResponse(BaseResponse):
    ok: bool
    first_name: str
    last_name: str
    lang: str
    tz: str
    uuid: UUID
    tenanat_id: str
    token: str


class PublicCompanyCounterResponse(BaseResponse):
    accounts: int
    limit: int


class RoleBasic(BaseModel):
    role_name: str

    class Config:
        orm_mode = True


class UserLoginOut(BaseResponse):  # OK
    auth_token: str
    first_name: str
    last_name: str
    tz: str
    lang: str
    uuid: UUID
    role_FK: RoleBasic


class UserIndexResponse(BaseResponse):
    first_name: str
    last_name: str
    email: str
    phone: str | None
    uuid: UUID
    is_active: bool
    is_verified: bool


class FileResponse(BaseResponse):
    uuid: UUID
    file_name: str
    extension: str
    mimetype: str
    size: int
    url: str | None


class SettingBase(BaseResponse):
    id: int
    account_id: int
    entity: str
    value: str
    value_type: str
    created_at: datetime | None
    updated_at: datetime | None


class IdeaSummaryResponse(BaseResponse):
    accepted: int
    pending: int
    rejected: int
    todo: int


class RoleSummaryResponse(BaseResponse):
    uuid: UUID
    role_title: str
    role_description: str
    is_custom: bool
    count: int
