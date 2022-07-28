import random
import secrets
from datetime import datetime, timedelta
from uuid import uuid4

from langcodes import standardize_tag
from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.orm import Session
from unidecode import unidecode

from app.models.models import User
from app.models.shared_models import PublicCompany, PublicUser
from app.schemas.requests import UserRegisterIn
from app.schemas.schemas import PubliCompanyAdd


def get_public_user_by_email(db: Session, email: str) -> PublicUser | None:
    return db.execute(select(PublicUser).where(PublicUser.email == email)).scalar_one_or_none()


def get_public_user_by_service_token(db: Session, token: str) -> PublicUser | None:
    return db.execute(
        select(PublicUser)
        .where(PublicUser.service_token == token)
        .where(PublicUser.is_active == False)
        .where(PublicUser.service_token_valid_to > datetime.utcnow())
    ).scalar_one_or_none()


def get_public_company_by_nip(db: Session, nip: str) -> PublicCompany | None:
    return db.execute(select(PublicCompany).where(PublicCompany.nip == nip)).scalar_one_or_none()


def generate_qr_id(db: Session, nip: str):
    allowed_chars = "abcdefghijkmnopqrstuvwxyz23456789"  # ABCDEFGHJKLMNPRSTUVWXYZ23456789
    company_ids = db.execute(select(PublicCompany.qr_id)).scalars().all()
    proposed_id = "".join(random.choice(allowed_chars) for x in range(3))
    while proposed_id in company_ids:
        proposed_id = "".join(random.choice(allowed_chars) for x in range(3))
    return proposed_id


def create_public_user(db: Session, user: UserRegisterIn) -> PublicUser:
    new_user = PublicUser(
        uuid=str(uuid4()),
        email=user.email.strip(),
        password=argon2.hash(user.password),
        service_token=secrets.token_hex(32),
        service_token_valid_to=datetime.utcnow() + timedelta(days=1),
        is_active=False,
        is_verified=False,
        tos=user.tos,
        tz=user.tz,
        lang=standardize_tag(user.lang),
        created_at=datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def create_public_company(db: Session, company: PubliCompanyAdd) -> PublicCompany:

    uuid = str(uuid4())
    tenanat_id = unidecode(company["short_name"]).lower() + "_" + uuid.replace("-", "")

    new_company = PublicCompany(
        uuid=uuid,
        name=company["name"],
        short_name=company["short_name"],
        nip=company["nip"],
        country=company["country"],
        city=company["city"],
        tenant_id=tenanat_id,
        qr_id=generate_qr_id(db, company["nip"]),
        created_at=datetime.utcnow(),
    )

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
            # service_token_valid_to=datetime.utcnow() + timedelta(days=1),
            auth_token=tenant_data["auth_token"],
            auth_token_valid_to=tenant_data["auth_token_valid_to"],
            user_role_id=tenant_data["role_id"],
            is_active=tenant_data["is_active"],
            is_verified=tenant_data["is_verified"],
            tos=tenant_data["tos"],
            tz=tenant_data["tz"],
            tenant_id=tenant_data["tenant_id"],
            lang=standardize_tag(tenant_data["lang"]),
            created_at=datetime.utcnow(),
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        print(e)
    return new_user


def get_tenant_user_by_auth_token(db: Session, token: str) -> User | None:
    return db.execute(
        select(User)
        .where(User.auth_token == token)
        .where(User.is_active == False)
        .where(User.service_token_valid_to > datetime.utcnow())
    ).scalar_one_or_none()
