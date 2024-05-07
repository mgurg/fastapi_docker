from sqlalchemy import Sequence

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from sqlalchemy import Sequence
from sqlalchemy.orm import Session

from app.api.repository.UserRepo import UserRepo
from app.crud import crud_auth
from app.db import engine
from app.models.models import User
from app.schemas.requests import UserCreateIn
from app.service.password import Password


class UserService:
    def __init__(self, user_repo: Annotated[UserRepo, Depends()]) -> None:
        self.user_repo = user_repo

    def add_user(self, user: UserCreateIn, tenant_id: str | None):
        if tenant_id is None:
            raise HTTPException(status_code=400, detail="Invalid Tenant")

        if (user.password is None) or (user.password_confirmation is None):
            raise HTTPException(status_code=400, detail="Password is missing")
        password = Password(user.password)
        is_password_ok = password.compare(user.password_confirmation)

        if is_password_ok is not True:
            raise HTTPException(status_code=400, detail=is_password_ok)

        db_user = self.user_repo.get_by_email(user.email)
        if db_user is not None:
            raise HTTPException(status_code=400, detail="User already exists")

        # db_role = crud_permission.get_role_by_uuid(db, user.user_role_uuid)
        # if db_role is None:
        #     raise HTTPException(status_code=400, detail="Invalid Role")

        user_uuid = str(uuid4())
        user_data = {
            "uuid": user_uuid,
            "email": user.email,
            "phone": user.phone,
            "password": password.hash(),
            "tos": True,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_role_id": 2,  # TODO
            "is_active": True,
            "is_verified": True,
            "is_visible": True,
            "tz": "Europe/Warsaw",
            "lang": "pl",
            "tenant_id": tenant_id,
            "created_at": datetime.now(timezone.utc),
        }

        self.user_repo.create(**user_data)

        schema_translate_map = {"tenant": "public"}
        connectable = engine.execution_options(schema_translate_map=schema_translate_map)
        with Session(autocommit=False, autoflush=False, bind=connectable) as db:
            public_user_data = {
                "uuid": user_uuid,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_active": True,
                "is_verified": True,
                "tos": True,
                "tenant_id": tenant_id,
                "tz": "Europe/Warsaw",
                "lang": "pl",
                "created_at": datetime.now(timezone.utc),
            }
            crud_auth.create_public_user(db, public_user_data)

    def get_user_by_uuid(self, uuid: UUID) -> User | None:
        db_user = self.user_repo.get_by_uuid(uuid)
        return db_user

    def get_all_users(
            self, offset: int, limit: int, sort_column: str, sort_order: str, search: str | None = None
    ) -> tuple[Sequence[User], int]:
        db_users, count = self.user_repo.get_users(offset, limit, sort_column, sort_order, search)

        return db_users, count

    def count_all_users(self) -> int:
        return self.user_repo.get_users_count()

    def get_user_by_auth_token(self, token: str) -> User | None:
        return self.user_repo.get_user_by_auth_token(token)
