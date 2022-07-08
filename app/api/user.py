from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate
from passlib.hash import argon2
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db import get_session
from app.model.model import User
from app.schema.schema import StandardResponse, UserCreateIn, UserIndexResponse
from app.service.bearer_auth import has_token
from app.service.password import Password

user_router = APIRouter()


@user_router.get("/", response_model=Page[UserIndexResponse], name="user:Profile")
async def user_get_all(
    *,
    session: Session = Depends(get_session),
    search: str = None,
    order: str = "asc",
    params: Params = Depends(),
    auth=Depends(has_token),
):

    all_filters = []

    if search is not None:
        all_filters.append(func.concat(User.first_name, " ", User.last_name).ilike(f"%{search}%"))

    users = (
        session.execute(
            select(User)
            .where(User.account_id == auth["account"])
            .where(User.is_active == True)
            .where(User.deleted_at.is_(None))
            .filter(*all_filters)
            .order_by(text(f"last_name {order}"))
        )
        .scalars()
        .all()
    )

    return paginate(users, params)


@user_router.get("/{user_uuid}", response_model=UserIndexResponse, name="user:Profile")
async def user_get_one(*, session: Session = Depends(get_session), user_uuid: UUID, auth=Depends(has_token)):
    db_user = session.execute(
        select(User)
        .where(User.account_id == auth["account"])
        .where(User.uuid == user_uuid)
        .where(User.is_active == True)
        .where(User.deleted_at.is_(None))
    ).scalar_one_or_none()

    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found")

    return db_user


@user_router.post("/", response_model=StandardResponse, name="user:Add")
async def user_add(*, session: Session = Depends(get_session), user: UserCreateIn, auth=Depends(has_token)):

    res = UserCreateIn.from_orm(user)

    if res.password is not None:
        password = Password(res.password)
        is_password_ok = password.compare(res.password_confirmation)

        if is_password_ok is True:
            pass_hash = argon2.hash(res.password)
        else:
            raise HTTPException(status_code=400, detail=is_password_ok)
    else:
        pass_hash = argon2.hash("string")

    new_user = User(
        account_id=auth["account"],
        email=res.email,
        password=pass_hash,
        first_name=res.first_name,
        last_name=res.last_name,
        service_token="t" * 32,
        service_token_valid_to=datetime.utcnow() + timedelta(days=7),
        user_role_id=2,
        created_at=datetime.utcnow(),
        is_active=True,
        is_verified=True,
        tz="Europe/Warsaw",
        lang="pl",
        uuid=str(uuid4()),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # postmark = PostmarkClient(server_token=settings.api_postmark)

    return {"ok": True}


@user_router.patch("/{user_uuid}", response_model=StandardResponse, name="user:Edit")
async def user_edit(
    *, session: Session = Depends(get_session), user_uuid: UUID, user: UserCreateIn, auth=Depends(has_token)
):

    db_user = session.execute(
        select(User)
        .where(User.account_id == auth["account"])
        .where(User.uuid == user_uuid)
        .where(User.deleted_at == None)
    ).scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.dict(exclude_unset=True)

    if "password" in user_data.keys():
        password = Password(user_data["password"])
        is_password_ok = password.compare(user_data["password_confirmation"])

        if is_password_ok is True:
            pass_hash = argon2.hash(user_data["password"])
        else:
            raise HTTPException(status_code=400, detail=is_password_ok)

        password = pass_hash
        del user_data["password"]
        del user_data["password_confirmation"]

    user_data["updated_at"] = datetime.utcnow()
    for key, value in user_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return {"ok": True}


@user_router.delete("/{user_uuid}", response_model=StandardResponse, name="user:Delete")
async def user_get_all(*, session: Session = Depends(get_session), user_uuid: UUID, auth=Depends(has_token)):

    db_user = session.execute(
        select(User)
        .where(User.account_id == auth["account"])
        .where(User.uuid == user_uuid)
        .where(User.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(db_user)
    session.commit()

    return {"ok": True}
