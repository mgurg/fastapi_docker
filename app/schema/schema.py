from datetime import datetime, time
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr


class StandardResponse(BaseModel):  # OK
    ok: bool


class Account(BaseModel):
    __tablename__ = "accounts"
    id: int | None
    uuid: UUID
    account_id: int
    company: str
    nip: str | None
    address: str | None
    company_id: str | None
    ideas_id: str | None

    class Config:
        orm_mode = True


class UserRegisterIn(BaseModel):  # OK
    email: EmailStr
    password: str
    password_confirmation: str
    tos: bool
    tz: str | None = "Europe/Warsaw"
    lang: str | None = "pl"

    class Config:
        orm_mode = True


class UserFirstRunIn(BaseModel):  # OK
    first_name: str
    last_name: str
    nip: str
    token: str

    class Config:
        orm_mode = True


class Role(BaseModel):
    __tablename__ = "roles"
    id: int | None
    uuid: UUID
    account_id: int
    role_name: str
    role_description: str
    hidden: bool
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None

    # permission: List["Permissions"] = Relationship(back_populates="role", link_model=RolePermissionLink)  # hasMany
    # users_FK: List["Users"] = Relationship(back_populates="role_FK")  # hasOne
    users_FK: List["User"]

    class Config:
        orm_mode = True


class PermissionsMini(BaseModel):
    name: str

    class Config:
        orm_mode = True


class UserSetPassIn(BaseModel):  # OK
    token: str
    password: str
    password_confirmation: str


class RoleBasic(BaseModel):
    role_name: str
    permission: List[PermissionsMini]

    class Config:
        orm_mode = True


class User(BaseModel):
    __tablename__ = "users"
    id: int
    account_id: int
    password: str
    email: EmailStr | None
    phone: str | None
    first_name: str | None
    last_name: str | None
    auth_token: str | None
    auth_token_valid_to: datetime | None
    is_active: bool
    is_verified: bool
    service_token: str | None
    service_token_valid_to: datetime | None
    tos: bool
    # user_role_id: int = Field(default=None, foreign_key="roles.id")
    # user_info_id:int | None = Field(default=None, foreign_key="users_info.id")
    tz: str
    lang: str
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    uuid: UUID

    role_FK: Role

    # usr_FK: List["Tasks"] = Relationship(back_populates="assignee")
    # role_FK: Optional["Roles"] = Relationship(back_populates="users_FK")  # hasOne
    class Config:
        orm_mode = True


class UserLoginIn(BaseModel):  # OK
    email: EmailStr
    password: str | None
    permanent: bool

    class Config:
        orm_mode = True


class UserLoginOut(BaseModel):  # OK
    auth_token: str
    first_name: str
    last_name: str
    tz: str
    lang: str
    uuid: UUID
    role_FK: RoleBasic

    class Config:
        orm_mode = True


class UserIndexResponse(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None
    uuid: UUID
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True


class UserCreateIn(BaseModel):  # OK
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    phone: str | None
    password: str | None
    password_confirmation: str | None
    is_verified: bool | None
    user_role_uuid: UUID | None

    class Config:
        orm_mode = True


class SettingBase(BaseModel):
    id: int
    account_id: int
    entity: str
    value: str
    value_type: str
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        orm_mode = True


class FileBasicInfo(BaseModel):
    uuid: UUID
    file_name: str
    extension: str
    mimetype: str
    size: int

    class Config:
        orm_mode = True


class IdeaIndexResponse(BaseModel):
    uuid: UUID
    color: str
    title: str
    description: str
    upvotes: int | None
    downvotes: int | None
    status: str | None
    created_at: datetime
    pictures: List[FileBasicInfo] | None

    class Config:
        orm_mode = True


class IdeaAddIn(BaseModel):
    title: str
    description: str
    color: str = "green"
    files: List[UUID] | None

    class Config:
        orm_mode = True


class IdeaEditIn(BaseModel):
    title: str | None
    description: str | None
    color: str | None
    status: str | None
    vote: str | None
    files: List[UUID] | None

    class Config:
        orm_mode = True


class IdeasVotesIn(BaseModel):
    idea_uuid: UUID
    vote: str

    class Config:
        orm_mode = True


class FileResponse(BaseModel):
    uuid: UUID
    file_name: str
    extension: str
    mimetype: str
    size: int

    # task: List[TaskBasicInfo]


class FileUrlResponse(BaseModel):
    uuid: UUID
    file_name: str
    extension: str
    mimetype: str
    size: int
    # url: HttpUrl

    # task: List[TaskBasicInfo]
