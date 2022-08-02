from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class UserRegisterIn(BaseRequest):
    email: EmailStr
    password: str
    password_confirmation: str
    tos: bool
    tz: str | None = "Europe/Warsaw"
    lang: str | None = "pl"


class UserFirstRunIn(BaseRequest):
    first_name: str
    last_name: str
    nip: str = "1234563218"
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
    title: str
    description: str
    color: str = "green"
    files: List[UUID] | None
