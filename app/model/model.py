from sqlalchemy import (
    Column,
    ForeignKey,
    Identity,
    Integer,
    MetaData,
    String,
    create_engine,
)
from sqlalchemy.dialects.postgresql import BOOLEAN, INTEGER, TIMESTAMP, UUID, VARCHAR
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, joinedload, relationship, sessionmaker

from app.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(UUID(), autoincrement=False, nullable=True)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)
    password = Column(VARCHAR(length=256), autoincrement=False, nullable=False)
    email = Column(VARCHAR(length=256), autoincrement=False, nullable=True)
    phone = Column(VARCHAR(length=16), autoincrement=False, nullable=True)
    first_name = Column(VARCHAR(length=100), autoincrement=False, nullable=True)
    last_name = Column(VARCHAR(length=100), autoincrement=False, nullable=True)
    auth_token = Column(VARCHAR(length=128), autoincrement=False, nullable=True, unique=True)
    auth_token_valid_to = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    is_active = Column(BOOLEAN(), autoincrement=False, nullable=False)
    service_token = Column("service_token", VARCHAR(length=100), autoincrement=False, nullable=True, unique=True)
    service_token_valid_to = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    tz = Column(VARCHAR(length=64), autoincrement=False, nullable=False)
    lang = Column(VARCHAR(length=8), autoincrement=False, nullable=False)
    user_role_id = Column(INTEGER(), autoincrement=False, nullable=True)
    tos = Column(BOOLEAN(), autoincrement=False, nullable=True)
    deleted_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(BOOLEAN(), autoincrement=False, nullable=False)
    # ForeignKeyConstraint(["user_role_id"], ["roles.id"], name="role_FK"),
    # PrimaryKeyConstraint("id", name="users_pkey"),
    # UniqueConstraint("email", name="users_email_key"),
    # UniqueConstraint("phone", name="users_phone_key"),


class Settings(Base):
    __tablename__ = "settings"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)
    entity = Column(VARCHAR(length=64), autoincrement=False, nullable=True)
    value = Column(VARCHAR(length=64), autoincrement=False, nullable=True)
    value_type = Column(VARCHAR(length=64), autoincrement=False, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
