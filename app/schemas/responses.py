from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, condecimal
from pydantic.color import Color


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


class CompanyInfoBasic(BaseResponse):
    name: str
    street: str | None
    city: str | None
    nip: str


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


class IssueSummaryResponse(BaseResponse):
    new: int
    accepted: int
    rejected: int
    assigned: int
    in_progress: int
    paused: int
    done: int


class RoleSummaryResponse(BaseResponse):
    uuid: UUID
    role_title: str
    role_description: str | None
    is_custom: bool
    count: int
    uncounted: int


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


class TagResponse(BaseResponse):
    uuid: UUID
    name: str
    color: Color | None = "#66b3ff"
    is_hidden: bool | None


class PartResponse(BaseResponse):
    uuid: UUID
    name: str
    description: str | None
    price: condecimal(max_digits=10, decimal_places=2)
    quantity: condecimal(max_digits=4, decimal_places=2)
    unit: str | None
    value: condecimal(max_digits=10, decimal_places=2)


class TagBasicInfo(BaseResponse):
    uuid: UUID
    name: str
    color: Color | None = "#66b3ff"


class QRCodeItemResponse(BaseResponse):
    resource: str
    qr_code_full_id: str
    ecc: str


class UserQrToken(BaseResponse):
    resource: str
    resource_uuid: UUID
    url: str
    anonymous_token: str


class GuideBasicResponse(BaseResponse):
    uuid: UUID
    name: str | None
    text: str | None


class ItemNameResponse(BaseResponse):
    uuid: UUID
    name: str | None


class GuideResponse(BaseResponse):
    uuid: UUID
    name: str | None
    text: str | None
    text_json: dict | None
    item: list[ItemNameResponse] | None
    # video_id: str | None


class ItemIndexResponse(BaseResponse):
    uuid: UUID
    name: str | None
    text: str | None
    text_json: dict | None


class EventTimelineResponse(BaseResponse):
    created_at: datetime
    author_name: str | None
    author_uuid: UUID | None
    action: str | None
    title: str | None
    description: str | None
    # value: str | None
    # resource: str | None
    # resource_uuid: UUID | None
    # thread_resource: str | None
    # thread_uuid: UUID | None


class ItemResponse(BaseResponse):
    uuid: UUID
    symbol: str | None
    name: str | None
    text: str | None
    text_json: dict | None
    files_item: list[FileBasicInfo] | None
    item_guides: list[GuideBasicResponse] | None
    users_item: list[UserBasicResponse] | None
    qr_code: QRCodeItemResponse | None


class IssueIndexResponse(BaseResponse):
    uuid: UUID
    symbol: str | None
    name: str | None
    text: str | None
    text_json: dict | None
    item: ItemNameResponse | None
    status: str | None
    priority: str | None
    color: str | None
    users_issue: list[UserBasicResponse] | None
    created_at: datetime


class IssueResponse(BaseResponse):
    uuid: UUID
    symbol: str | None
    name: str | None
    text: str | None
    text_json: dict | None
    item: ItemNameResponse | None
    status: str | None
    priority: str | None
    color: str | None
    users_issue: list[UserBasicResponse] | None
    files_issue: list[FileBasicInfo] | None
    tags_issue: list[TagBasicInfo] | None
    # item_guides: list[GuideBasicResponse] | None


class UserVerifyToken(BaseResponse):
    auth_token_valid_to: datetime
    first_name: str
    last_name: str
    tz: str
    lang: str
    uuid: UUID
    role_FK: RoleLoginBasic


class BasicItems(BaseResponse):
    uuid: UUID
    name: str | None


class GuideIndexResponse(BaseResponse):
    uuid: UUID
    name: str | None
    text: str | None
    text_json: dict | None
    # video_id: str | None
    # video_json: dict | None
    files_guide: list[FileBasicInfo] | None
    item: list[BasicItems] | None
    qr_code: QRCodeItemResponse | None


class IdeaIndexResponse(BaseResponse):
    uuid: UUID
    color: str
    name: str
    text: str
    text_json: dict | None
    upvotes: int | None
    downvotes: int | None
    status: str | None
    created_at: datetime
    files_idea: list[FileBasicInfo] | None


class PermissionsFull(BaseResponse):
    uuid: UUID
    name: str
    title: str
    description: str
    group: str | None


class RolePermissionFull(BaseResponse):
    role_name: str
    role_description: str | None
    role_title: str
    is_custom: bool
    permission: list[PermissionsFull] | None


class SettingNotificationResponse(BaseResponse):
    sms_notification_level: str | None
    email_notification_level: str | None


class StatsIssuesCounterResponse(BaseResponse):
    new: int
    accepted: int
    rejected: int
    assigned: int
    in_progress: int
    paused: int
    done: int
