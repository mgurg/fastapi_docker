import uuid as uuid
from datetime import datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import EmailStr, Json
from sqlmodel import Field, Relationship, SQLModel


class StandardResponse(SQLModel):  # OK
    ok: bool


class Users(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int
    password: str
    email: Optional[EmailStr]
    phone: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    auth_token: Optional[str]
    auth_token_valid_to: Optional[datetime]
    is_active: int
    service_token: Optional[str]
    service_token_valid_to: Optional[datetime]
    # user_role_id: int = Field(default=None, foreign_key="roles.id")
    # user_info_id: Optional[int] = Field(default=None, foreign_key="users_info.id")
    tz: str
    lang: str
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    uuid: uuid.UUID


class UserCreateIn(SQLModel):  # OK
    email: EmailStr
    password: Optional[str]
    password_confirmation: Optional[str]
    first_name: str
    last_name: str
    user_role_uuid: Optional[uuid.UUID]
    # details: Optional[UsersDetailsCreate]


class UserRegisterIn(SQLModel):  # OK
    email: EmailStr
    password: str
    password_confirmation: str
    tos: bool
    tz: Optional[str]
    lang: Optional[str]
