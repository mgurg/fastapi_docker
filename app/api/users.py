import codecs
import csv
import io
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.crud import crud_auth, crud_permission, crud_users
from app.db import engine, get_db
from app.models.models import User
from app.schemas.requests import UserCreateIn
from app.schemas.responses import StandardResponse, UserIndexResponse
from app.service.bearer_auth import has_token
from app.service.password import Password

user_router = APIRouter()

CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[AsyncSession, Depends(get_db)]


@user_router.get("/", response_model=Page[UserIndexResponse])
async def user_get_all(
    *,
    db: UserDB,
    params: Annotated[Params, Depends()],
    auth_user: CurrentUser,
    # search: Annotated[str | None, Query(max_length=50)] = None,
    search: str | None = None,
    field: str = "name",
    order: str = "asc",
):
    if field not in ["first_name", "last_name", "created_at"]:
        field = "last_name"

    db_users_query = crud_users.get_users(field, order, search)

    # result = db.execute(db_users_query)  # await db.execute(query)
    # db_users = result.scalars().all()

    return paginate(db, db_users_query)


@user_router.get("/count")
def get_users_count(*, db: UserDB, auth_user: CurrentUser):
    db_user_cnt = crud_users.get_user_count(db)

    return db_user_cnt


@user_router.get("/export")
def get_export_users(*, db: UserDB, auth_user: CurrentUser):
    db_users_query = crud_users.get_users("last_name", "asc")
    result = db.execute(db_users_query)  # await db.execute(query)
    db_users = result.scalars().all()

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

    # https://github.com/Nasajon/fidesops/blob/03800a1e1c654eb34739d7097d74b37e318bcb50/src/fidesops/api/v1/endpoints/privacy_request_endpoints.py#L3

    # with open('users.csv', 'w', newline='') as csvfile:
    #     csv_writer = csv.writer(csvfile, delimiter=";")
    #     csv_writer.writerow(["First Name","Last Name","Email"])


@user_router.post("/import")
def get_import_users(*, db: UserDB, auth_user: CurrentUser, file: UploadFile | None = None):
    if not file:
        raise HTTPException(status_code=400, detail="No file sent")

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
        # print(rows)

    file.file.close()

    print(list(data.values()))

    # crud_users.bulk_insert(db, list(data.values()))

    # https://stackoverflow.com/a/70655118

    return data


@user_router.get("/{user_uuid}", response_model=UserIndexResponse)
def user_get_one(*, db: UserDB, user_uuid: UUID, auth_user: CurrentUser):
    user = crud_users.get_user_by_uuid(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.post("/", response_model=StandardResponse)  # , response_model=User , auth_user: CurrentUser
def user_add(*, db: UserDB, user: UserCreateIn, request: Request, auth_user: CurrentUser):
    db_user = crud_users.get_user_by_email(db, user.email)
    if db_user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    if (user.password is None) or (user.password_confirmation is None):
        raise HTTPException(status_code=400, detail="Password is missing")

    password = Password(user.password)
    is_password_ok = password.compare(user.password_confirmation)

    if is_password_ok is not True:
        raise HTTPException(status_code=400, detail=is_password_ok)

    # user_data = user.dict(exclude_unset=True)
    # user_data.pop("password_confirmation", None)

    db_role = crud_permission.get_role_by_uuid(db, user.user_role_uuid)
    if db_role is None:
        raise HTTPException(status_code=400, detail="Invalid Role")

    tenant_id = request.headers.get("tenant", None)
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="Invalid Tenant")

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

    crud_users.create_user(db, user_data)

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

    return {"ok": True}


@user_router.patch("/{user_uuid}", response_model=StandardResponse)
def user_edit(*, db: UserDB, user_uuid: UUID, user: UserCreateIn, auth_user: CurrentUser):
    db_user = crud_users.get_user_by_uuid(db, user_uuid)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    current_email = db_user.email
    print(current_email)

    if user.email:
        email_db_user = crud_users.get_user_by_email(db, user.email)
        if (email_db_user is not None) and (email_db_user.id != db_user.id):
            raise HTTPException(status_code=400, detail="Email is assigned to other user")

    user_data = user.dict(exclude_unset=True)

    if ("password" in user_data.keys()) and (user_data["password"] is not None):
        password = Password(user_data["password"])
        is_password_ok = password.compare(user_data["password_confirmation"])

        if is_password_ok is not True:
            raise HTTPException(status_code=400, detail=is_password_ok)

        user_data["password"] = password.hash()
        user_data["updated_at"] = datetime.now(timezone.utc)
        user_data.pop("password_confirmation", None)

    if "user_role_uuid" in user_data.keys():
        db_role = crud_permission.get_role_by_uuid(db, user.user_role_uuid)
        if db_role is None:
            raise HTTPException(status_code=400, detail="Invalid Role")
        user_data["user_role_id"] = db_role.id
        user_data.pop("user_role_uuid", None)

    # print(user_data)
    crud_users.update_user(db, db_user, user_data)

    # UPDATE PUBLIC USER INFO
    if ("email" in user_data.keys()) and (user_data["email"] is not None):
        schema_translate_map = {"tenant": "public"}
        connectable = engine.execution_options(schema_translate_map=schema_translate_map)
        with Session(autocommit=False, autoflush=False, bind=connectable) as public_db:
            db_public_user = crud_auth.get_public_user_by_email(public_db, current_email)
            # print(current_email, db_public_user.id)
            # print({"email": user_data["email"]})
            crud_auth.update_public_user(public_db, db_public_user, {"email": user_data["email"]})

    return {"ok": True}


@user_router.delete("/{user_uuid}", response_model=StandardResponse)
def user_delete(*, db: UserDB, user_uuid: UUID, auth_user: CurrentUser, force: bool = False):
    db_user = crud_users.get_user_by_uuid(db, user_uuid)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    email = db_user.email

    if force is True:
        db.delete(db_user)
        db.commit()
    else:
        crud_users.update_user(db, db_user, {"deleted_at": datetime.now(timezone.utc)})

    schema_translate_map = {"tenant": "public"}
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable) as db:
        db_public_user = crud_auth.get_public_user_by_email(db, email)

        if db_public_user:
            db.delete(db_public_user)
            db.commit()

    return {"ok": True}
