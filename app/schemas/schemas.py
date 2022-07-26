from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr


class StandardResponse(BaseModel):  # OK
    ok: bool


class PubliCompanyAdd(BaseModel):  # OK
    name: str
    short_name: str
    nip: str
    country: str
    city: str


class BookBase(BaseModel):
    __tablename__ = "books"
    id: int | None
    title: str | None
    author: str | None

    class Config:
        orm_mode = True


class RoleBase(BaseModel):
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
    users_FK: List["UserBase"]

    class Config:
        orm_mode = True


class PermissionsMini(BaseModel):
    name: str

    class Config:
        orm_mode = True


class RoleBasic(BaseModel):
    role_name: str
    permission: List[PermissionsMini]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
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

    role_FK: RoleBase

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
    tenant_id: str | None

    class Config:
        orm_mode = True
