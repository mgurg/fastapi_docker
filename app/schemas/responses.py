from datetime import datetime
from typing import List
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
    tenant_id: str
    token: str


class PublicCompanyCounterResponse(BaseResponse):
    accounts: int
    limit: int


class RoleBasic(BaseResponse):
    uuid: UUID
    role_name: str
    role_title: str


class PermissionsLoginBasic(BaseResponse):
    name: str


class RoleLoginBasic(BaseResponse):
    role_name: str
    permission: list[PermissionsLoginBasic]


class UserLoginOut(BaseResponse):
    auth_token: str
    auth_token_valid_to: datetime
    first_name: str
    last_name: str
    tz: str
    lang: str
    uuid: UUID
    role_FK: RoleLoginBasic
    tenant_id: str | None


class UserBasicResponse(BaseResponse):
    uuid: UUID
    first_name: str
    last_name: str


class UserIndexResponse(BaseResponse):
    first_name: str
    last_name: str
    email: str
    phone: str | None
    uuid: UUID
    is_active: bool
    is_verified: bool
    role_FK: RoleBasic


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


class PermissionResponse(BaseResponse):
    uuid: UUID
    group: str
    title: str
    name: str
    description: str


class GroupSummaryResponse(BaseResponse):
    uuid: UUID
    symbol: str | None
    name: str
    description: str | None
    # count: int


class GroupResponse(BaseResponse):
    uuid: UUID
    symbol: str | None
    name: str | None
    description: str | None
    users: list[UserBasicResponse]


class FileBasicInfo(BaseResponse):
    uuid: UUID
    file_name: str
    extension: str
    mimetype: str
    size: int
    url: str | None


class ItemIndexResponse(BaseResponse):
    uuid: UUID
    name: str | None
    description: str | None
    description_jsonb: dict | None


class GuideBasicResponse(BaseResponse):
    uuid: UUID
    name: str | None
    text: str | None


class QRCodeItemResponse(BaseResponse):
    resource: str
    qr_code_full_id: str
    ecc: str


class ItemResponse(BaseResponse):
    uuid: UUID
    name: str | None
    description: str | None
    description_jsonb: dict | None
    files_item: List[FileBasicInfo] | None
    item_guides: List[GuideBasicResponse] | None
    qr_code: QRCodeItemResponse | None


class GuideResponse(BaseResponse):
    uuid: UUID
    name: str | None
    text: str | None
    text_jsonb: dict | None
    video_id: str | None


class UserQrToken(BaseResponse):
    url: str
    anonymous_token: str


class UserVerifyToken(BaseResponse):
    auth_token_valid_to: datetime
    first_name: str
    last_name: str
    tz: str
    lang: str
    uuid: UUID
    role_FK: RoleLoginBasic
