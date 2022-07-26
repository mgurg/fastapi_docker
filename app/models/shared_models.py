from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

metadata = sa.MetaData(schema="shared")
Base = declarative_base(metadata=metadata)


class Tenant(Base):
    __tablename__ = "tenants"
    id = sa.Column(
        sa.Integer(),
        sa.Identity(),
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    uuid = sa.Column(UUID(as_uuid=True), default=uuid4(), unique=True)
    name = sa.Column("name", sa.String(128), nullable=True)
    schema = sa.Column(sa.String(128), nullable=True)
    schema_header_id = sa.Column("schema_header_id", sa.String(128), nullable=True)

    __table_args__ = {"schema": "public"}


class PublicUser(Base):
    __tablename__ = "public_users"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    email = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    password = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    service_token = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True, unique=True)
    service_token_valid_to = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    is_active = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    is_verified = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    tos = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    tenant_id = sa.Column(sa.VARCHAR(length=64), autoincrement=False, nullable=True)
    tz = sa.Column(sa.VARCHAR(length=64), autoincrement=False, nullable=True, unique=True)
    lang = sa.Column(sa.VARCHAR(length=8), autoincrement=False, nullable=True, unique=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    __table_args__ = {"schema": "public"}


class PublicCompany(Base):
    __tablename__ = "public_companies"
    id = sa.Column(
        sa.INTEGER(),
        sa.Identity(),
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    name = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    short_name = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    nip = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=True, unique=True)
    country = sa.Column(sa.VARCHAR(length=128), autoincrement=False, nullable=True, unique=True)
    city = sa.Column(sa.VARCHAR(length=128), autoincrement=False, nullable=True, unique=True)
    tenant_id = sa.Column(sa.VARCHAR(length=64), autoincrement=False, nullable=True)
    qr_id = sa.Column(sa.VARCHAR(length=32), autoincrement=False, nullable=True, unique=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    __table_args__ = {"schema": "public"}
