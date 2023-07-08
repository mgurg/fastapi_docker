from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, condecimal
from pydantic_extra_types.color import Color


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


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
    tenant_id: str | None = None


class CompanyInfoBasic(BaseResponse):
    name: str
    street: str | None = None
    city: str | None = None
    nip: str


class UserBasicResponse(BaseResponse):
    uuid: UUID
    first_name: str
    last_name: str


class UserIndexResponse(BaseResponse):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
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
    url: str | None = None


class SettingBase(BaseResponse):
    id: int
    account_id: int
    entity: str
    value: str
    value_type: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


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
    role_description: str | None = None
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
    symbol: str | None = None
    name: str
    description: str | None = None
    # count: int


class GroupResponse(BaseResponse):
    uuid: UUID
    symbol: str | None = None
    name: str | None = None
    description: str | None = None
    users: list[UserBasicResponse]


class FileBasicInfo(BaseResponse):
    uuid: UUID
    file_name: str
    extension: str
    mimetype: str
    size: int
    url: str | None = None


class TagResponse(BaseResponse):
    uuid: UUID
    name: str
    color: Color | None = "#66b3ff"
    is_hidden: bool | None = None


class PartResponse(BaseResponse):
    uuid: UUID
    name: str
    description: str | None = None
    price: condecimal(max_digits=10, decimal_places=2)
    quantity: condecimal(max_digits=4, decimal_places=2)
    unit: str | None = None
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
    name: str | None = None
    text: str | None = None


class ItemNameResponse(BaseResponse):
    uuid: UUID
    name: str | None = None


class GuideResponse(BaseResponse):
    uuid: UUID
    name: str | None = None
    text: str | None = None
    text_json: dict | None = None
    item: list[ItemNameResponse] | None = None
    # video_id: str | None


class ItemIndexResponse(BaseResponse):
    uuid: UUID
    name: str | None = None
    text: str | None = None
    text_json: dict | None = None


class EventTimelineResponse(BaseResponse):
    created_at: datetime
    author_name: str | None = None
    author_uuid: UUID | None = None
    action: str | None = None
    title: str | None = None
    description: str | None = None
    # value: str | None
    # resource: str | None
    # resource_uuid: UUID | None
    # thread_resource: str | None
    # thread_uuid: UUID | None


class ItemResponse(BaseResponse):
    uuid: UUID
    symbol: str | None = None
    name: str | None = None
    text: str | None = None
    text_json: dict | None = None
    files_item: list[FileBasicInfo] | None = None
    item_guides: list[GuideBasicResponse] | None = None
    users_item: list[UserBasicResponse] | None = None
    qr_code: QRCodeItemResponse | None = None


class IssueIndexResponse(BaseResponse):
    uuid: UUID
    symbol: str | None = None
    name: str | None = None
    text: str | None = None
    text_json: dict | None = None
    item: ItemNameResponse | None = None
    status: str | None = None
    priority: str | None = None
    color: str | None = None
    users_issue: list[UserBasicResponse] | None = None
    created_at: datetime


class IssueResponse(BaseResponse):
    uuid: UUID
    symbol: str | None = None
    name: str | None = None
    text: str | None = None
    text_json: dict | None = None
    item: ItemNameResponse | None = None
    status: str | None = None
    priority: str | None = None
    color: str | None = None
    users_issue: list[UserBasicResponse] | None = None
    files_issue: list[FileBasicInfo] | None = None
    tags_issue: list[TagBasicInfo] | None = None
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
    name: str | None = None


class GuideIndexResponse(BaseResponse):
    uuid: UUID
    name: str | None = None
    text: str | None = None
    text_json: dict | None = None
    # video_id: str | None
    # video_json: dict | None
    files_guide: list[FileBasicInfo] | None = None
    item: list[BasicItems] | None = None
    qr_code: QRCodeItemResponse | None = None


class IdeaIndexResponse(BaseResponse):
    uuid: UUID
    color: str
    name: str
    text: str
    text_json: dict | None = None
    upvotes: int | None = None
    downvotes: int | None = None
    status: str | None = None
    created_at: datetime
    files_idea: list[FileBasicInfo] | None = None


class PermissionsFull(BaseResponse):
    uuid: UUID
    name: str
    title: str
    description: str
    group: str | None = None


class RolePermissionFull(BaseResponse):
    role_name: str
    role_description: str | None = None
    role_title: str
    is_custom: bool
    permission: list[PermissionsFull] | None = None


class SettingNotificationResponse(BaseResponse):
    sms_notification_level: str | None = None
    email_notification_level: str | None = None


class StatsIssuesCounterResponse(BaseResponse):
    new: int
    accepted: int
    rejected: int
    assigned: int
    in_progress: int
    paused: int
    done: int
