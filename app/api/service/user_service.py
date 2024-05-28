import codecs
import csv
import io
import sys
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy import Sequence
from starlette.responses import StreamingResponse
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
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Invalid role: {user.role_uuid}")

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

    def edit_user(self, user_uuid: UUID, user: UserCreateIn):
        db_user = self.user_repo.get_by_uuid(user_uuid)
        if db_user is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"User {user_uuid} not found")

        if user.email:
            email_db_user = self.user_repo.get_by_email(db_user.email)
            if (email_db_user is not None) and (email_db_user.id != db_user.id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail=f"Email {user.email} is already assigned to other user"
                )

        user_data = user.model_dump(exclude_unset=True)

        if ("password" in user_data.keys()) and (user_data["password"] is not None):
            password = Password(user_data["password"])
            is_password_ok = password.compare(user_data["password_confirmation"])

            if is_password_ok is not True:
                raise HTTPException(status_code=400, detail=is_password_ok)

            user_data["password"] = password.hash()
            user_data["updated_at"] = datetime.now(timezone.utc)
            user_data.pop("password_confirmation", None)

        if "role_uuid" in user_data.keys():
            db_role = self.role_repo.get_by_uuid(user.role_uuid)
            if db_role is None:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Invalid role: {user.role_uuid}")
            user_data["user_role_id"] = db_role.id
            user_data.pop("role_uuid", None)

        self.user_repo.update(db_user.id, **user_data)
        # UPDATE PUBLIC USER INFO
        if ("email" in user_data.keys()) and (user_data["email"] is not None) and ("pytest" not in sys.modules):
            self.update_public_user(user_uuid, {"email": user_data["email"]})

    def update_public_user(self, user_uuid, public_user_data):
        db_public_user = self.public_user_repo.get_by_uuid(user_uuid)
        self.public_user_repo.update(db_public_user.id, **public_user_data)

    def get_user_by_uuid(self, uuid: UUID) -> User | None:
        db_user = self.user_repo.get_by_uuid(uuid)
        if not db_user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
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

    def export(self):
        db_users, count = self.user_repo.get_users(0, 50, "last_name", "asc", None)

        f = io.StringIO()
        csv_file = csv.writer(f, delimiter=";")
        csv_file.writerow(["First Name", "Last Name", "Email"])
        for u in db_users:
            csv_file.writerow([u.first_name, u.last_name, u.email])

        f.seek(0)
        response = StreamingResponse(f, media_type="text/csv")
        filename = f"users_{datetime.today().strftime('%Y-%m-%d')}.csv"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    def import_users(self, file: UploadFile):
        csv_reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"), delimiter=";")

        data = {}
        for idx, rows in enumerate(csv_reader):
            key = idx  # Assuming a column named 'Id' to be the primary key
            data[key] = rows
            data[key]["uuid"] = str(uuid4())
            data[key]["is_active"] = True
            data[key]["is_verified"] = True
            data[key]["tz"] = "Europe/Warsaw"
            data[key]["lang"] = "pl"
            data[key]["phone"] = None

        file.file.close()

        print(list(data.values()))

        # crud_users.bulk_insert(db, list(data.values()))

        # https://stackoverflow.com/a/70655118

        return data
