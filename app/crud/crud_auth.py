import base64
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.db import engine
from app.models.models import User
from app.models.shared_models import PublicCompany, PublicUser


def get_public_user_by_email(db: Session, email: str) -> PublicUser | None:
    query = select(PublicUser).where(PublicUser.email == email)

    result = db.execute(query)  # await db.execute(query)

    return result.scalar_one_or_none()


def get_public_user_by_service_token(db: Session, token: str) -> PublicUser | None:
    query = (
        select(PublicUser)
        .where(PublicUser.service_token == token)
        .where(PublicUser.is_active == False)  # noqa: E712
        .where(PublicUser.service_token_valid_to > datetime.now(timezone.utc))
    )

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_public_active_user_by_service_token(db: Session, token: str) -> PublicUser | None:
    query = (
        select(PublicUser)
        .where(PublicUser.service_token == token)
        .where(PublicUser.is_active == True)  # noqa: E712
        .where(PublicUser.service_token_valid_to > datetime.now(timezone.utc))
    )

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_public_company_count(db: Session) -> int | None:
    query = select(func.count(PublicCompany.id))

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_public_company_by_nip(db: Session, nip: str) -> PublicCompany | None:
    query = select(PublicCompany).where(PublicCompany.nip == nip)
    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_public_company_by_qr_id(db: Session, qr_id: str) -> PublicCompany | None:
    query = select(PublicCompany).where(PublicCompany.qr_id == qr_id)
    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_public_company_by_tenant_id(db: Session, tenant_id: str) -> PublicCompany | None:
    query = select(PublicCompany).where(PublicCompany.tenant_id == tenant_id)
    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def get_schemas_from_public_company(db: Session):
    query = select(distinct(PublicCompany.tenant_id))
    result = db.execute(query)  # await db.execute(query)
    return result.scalars().all()


def create_public_user(db: Session, public_user: dict) -> PublicUser:
    new_user = PublicUser(**public_user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def create_public_company(db: Session, company: dict) -> PublicCompany:
    new_company = PublicCompany(**company)
    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


def update_public_user(db: Session, db_user: PublicUser, update_data: dict) -> PublicUser:
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# def update_tenant_user(db: Session, db_user: User, update_data: dict) -> User:
#     try:
#         for key, value in update_data.items():
#             setattr(db_user, key, value)

#         db.add(db_user)
#         db.commit()
#         db.refresh(db_user)
#     except Exception as e:
#         print("#####", e)
#     return db_user


def create_tenant_user(db: Session, tenant_data) -> User:
    # try:
    new_user = User(**tenant_data)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # except Exception as e:
    #     print(e)
    return new_user


def get_tenant_user_by_auth_token(db: Session, token: str) -> User | None:
    try:
        query = (
            select(User)
            .where(User.auth_token == token)
            .where(User.is_active == True)  # noqa: E712
            .where(User.auth_token_valid_to > datetime.now(timezone.utc))
        )

        result = db.execute(query)  # await db.execute(query)
        db_tenant_user = result.scalar_one_or_none()

        return db_tenant_user
    except Exception as e:
        print(e)


def get_anonymous_user(db: Session) -> User:
    query = select(User).where(User.email == "anonymous@example.com").where(User.is_visible == False)  # noqa: E712

    result = db.execute(query)  # await db.execute(query)
    return result.scalar_one_or_none()


def generate_base64_token(token: str) -> str:
    message_bytes = token.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode("ascii")


def get_public_company_from_tenant(tenant_id: str) -> PublicCompany | None:
    company = None
    schema_translate_map = {"tenant": "public"}
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable) as public_db:
        company = get_public_company_by_tenant_id(public_db, tenant_id)
    if not company:
        raise HTTPException(status_code=400, detail="Unknown Company!")

    return company
