import sys
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from sqlalchemy import Sequence
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.api.repository.PublicUserRepo import PublicUserRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo
from app.models.models import User
from app.schemas.requests import UserCreateIn
from app.service.password import Password


class UserService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends()],
        role_repo: Annotated[RoleRepo, Depends()],
        public_user_repo: Annotated[PublicUserRepo, Depends()],
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.public_user_repo = public_user_repo

    def add_user(self, user: UserCreateIn, tenant_id: str | None):
        if tenant_id is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid Tenant")

        if (user.password is None) or (user.password_confirmation is None):
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Password is missing")
        password = Password(user.password)
        is_password_ok = password.compare(user.password_confirmation)

        if is_password_ok is not True:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=is_password_ok)

        db_user = self.user_repo.get_by_email(user.email)
        if db_user is not None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already exists")

        db_role = self.role_repo.get_by_uuid(user.role_uuid)
        if db_role is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid Role")

        user_uuid = str(uuid4())
        user_data = {
            "uuid": user_uuid,
            "email": user.email,
            "phone": user.phone,
            "password": password.hash(),
            "tos": True,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_role_id": db_role.id,
            "is_active": True,
            "is_verified": True,
            "is_visible": True,
            "tz": "Europe/Warsaw",
            "lang": "pl",
            "tenant_id": tenant_id,
            "created_at": datetime.now(timezone.utc),
        }

        self.user_repo.create(**user_data)

        if "pytest" not in sys.modules:
            self.create_public_user(tenant_id, user, user_uuid)

    def create_public_user(self, tenant_id, user, user_uuid):
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

        self.public_user_repo.create(**public_user_data)

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

    def delete_user(self, user_uuid: UUID, force: bool = False):
        db_user = self.user_repo.get_by_uuid(user_uuid)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        email = db_user.email

        if force is True:
            self.user_repo.delete(db_user.id)
        else:
            self.user_repo.update(db_user.id, **{"deleted_at": datetime.now(timezone.utc)})

        if "pytest" not in sys.modules:
            self.delete_public_user(user_uuid)  # TODO: not delete if Force is False?

    def delete_public_user(self, user_uuid: UUID):
        public_db_user = self.public_user_repo.get_by_uuid(user_uuid)
        if not public_db_user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Public user {user_uuid} not found")

        self.public_user_repo.delete(public_db_user.id)
        # schema_translate_map = {"tenant": "public"}
        # connectable = engine.execution_options(schema_translate_map=schema_translate_map)
        # with Session(autocommit=False, autoflush=False, bind=connectable) as db:
        #     db_public_user = crud_auth.get_public_user_by_email(db, email)
        #
        #     if db_public_user:
        #         db.delete(db_public_user)
        #         db.commit()
