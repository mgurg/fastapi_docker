import uuid as uuid
from datetime import datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import EmailStr, Json
from sqlmodel import Field, Relationship, SQLModel


class Users(SQLModel, table=True):
    __tablename__ = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int
    email: EmailStr
    # password: str
    # auth_token: Optional[str]
    # auth_token_valid_to: Optional[datetime]
    # is_active: int
    # service_token: Optional[str]
    # service_token_valid_to: Optional[datetime]
    # first_name: Optional[str]
    # last_name: Optional[str]
    # user_role_id: int = Field(default=None, foreign_key="roles.id")
    # user_info_id: Optional[int] = Field(default=None, foreign_key="users_info.id")
    # tz: str
    # lang: str
    # deleted_at: Optional[datetime]
    # created_at: datetime
    # updated_at: Optional[datetime]
    # uuid: uuid.UUID
