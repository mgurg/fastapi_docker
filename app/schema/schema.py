import uuid as uuid
from datetime import datetime, time

from pydantic import BaseModel, EmailStr


class Users(BaseModel):
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
    # user_role_id: int = Field(default=None, foreign_key="roles.id")
    # user_info_id: Optional[int] = Field(default=None, foreign_key="users_info.id")
    tz: str
    lang: str
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    uuid: uuid.UUID

    # usr_FK: List["Tasks"] = Relationship(back_populates="assignee")
    # role_FK: Optional["Roles"] = Relationship(back_populates="users_FK")  # hasOne


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
