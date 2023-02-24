import base64
from datetime import datetime, timezone
from uuid import uuid4

from langcodes import standardize_tag
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models.models import User
from app.models.shared_models import PublicCompany, PublicUser


def get_public_user_by_email(db: Session, email: str) -> PublicUser | None:
    return db.execute(select(PublicUser).where(PublicUser.email == email)).scalar_one_or_none()


def get_public_user_by_service_token(db: Session, token: str) -> PublicUser | None:
    return db.execute(
        select(PublicUser)
        .where(PublicUser.service_token == token)
        .where(PublicUser.is_active == False)  # noqa: E712
        .where(PublicUser.service_token_valid_to > datetime.now(timezone.utc))
    ).scalar_one_or_none()


def get_public_company_count(db: Session) -> int:
    return db.execute(select(func.count(PublicCompany.id))).scalar_one_or_none()


def get_public_company_by_nip(db: Session, nip: str) -> PublicCompany | None:
    return db.execute(select(PublicCompany).where(PublicCompany.nip == nip)).scalar_one_or_none()


def get_public_company_by_qr_id(db: Session, qr_id: str) -> PublicCompany | None:
    return db.execute(select(PublicCompany).where(PublicCompany.qr_id == qr_id)).scalar_one_or_none()


def get_public_company_by_tenant_id(db: Session, tenant_id: str) -> PublicCompany | None:
    return db.execute(select(PublicCompany).where(PublicCompany.tenant_id == tenant_id)).scalar_one_or_none()


def get_schemas_from_public_company(db: Session):
    return db.execute(select(distinct(PublicCompany.tenant_id))).scalars().all()


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


def update_tenant_user(db: Session, db_user: User, update_data: dict) -> User:
    try:
        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print("#####", e)
    return db_user


def create_tenant_user(db: Session, tenant_data) -> User:
    try:
        new_user = User(
            uuid=str(uuid4()),
            first_name=tenant_data["first_name"],
            last_name=tenant_data["last_name"],
            email=tenant_data["email"],
            password=tenant_data["password"],
            # service_token=secrets.token_hex(32),
            # service_token_valid_to=datetime.now(timezone.utc) + timedelta(days=1),
            auth_token=tenant_data["auth_token"],
            auth_token_valid_to=tenant_data["auth_token_valid_to"],
            user_role_id=tenant_data["role_id"],
            is_active=tenant_data["is_active"],
            is_verified=tenant_data["is_verified"],
            tos=tenant_data["tos"],
            tz=tenant_data["tz"],
            tenant_id=tenant_data["tenant_id"],
            lang=standardize_tag(tenant_data["lang"]),
            created_at=datetime.now(timezone.utc),
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        print(e)
    return new_user


def get_tenant_user_by_auth_token(db: Session, token: str) -> User | None:
    try:
        db_tenant_user = db.execute(
            select(User)
            .where(User.auth_token == token)
            .where(User.is_active == True)  # noqa: E712
            .where(User.auth_token_valid_to > datetime.now(timezone.utc))
        ).scalar_one_or_none()
        return db_tenant_user
    except Exception as e:
        print(e)


def generate_base64_token(token: str) -> str:
    message_bytes = token.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode("ascii")
