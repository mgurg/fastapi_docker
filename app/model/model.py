from sqlalchemy import (
    Column,
    ForeignKey,
    Identity,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)
from sqlalchemy.dialects.postgresql import (
    BOOLEAN,
    INTEGER,
    TEXT,
    TIMESTAMP,
    UUID,
    VARCHAR,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, joinedload, relationship, sessionmaker

from app.db import Base


class Account(Base):
    __tablename__ = "accounts"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    company = Column(VARCHAR(length=256), autoincrement=False, nullable=True)
    registered_at = Column("registered_at", TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    nip = Column(VARCHAR(length=32), autoincrement=False, nullable=True)
    address = Column(VARCHAR(), autoincrement=False, nullable=True)
    company_id = Column(VARCHAR(length=8), autoincrement=False, nullable=True)
    ideas_id = Column(VARCHAR(length=8), autoincrement=False, nullable=True)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)


# class RolePermissionLink(Base):
#     __tablename__ = "roles_permissions_link"
#     role_id = Column(INTEGER(), autoincrement=False, nullable=False)
#     permission_id = Column(INTEGER(), autoincrement=False, nullable=False)
# ForeignKeyConstraint(["permission_id"], ["permissions.id"], name="roles_permissions_link_fk_1"),
# ForeignKeyConstraint(["role_id"], ["roles.id"], name="roles_permissions_link_fk"),
# PrimaryKeyConstraint("role_id", "permission_id", name="roles_permissions_link_pkey"),

role_permission_rel = Table(
    "roles_permissions_link",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), autoincrement=False, nullable=False, primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), autoincrement=False, nullable=False, primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = Column("uuid", UUID(as_uuid=True), autoincrement=False, nullable=True)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)
    role_name = Column(VARCHAR(length=100), autoincrement=False, nullable=True)
    role_description = Column(VARCHAR(length=100), autoincrement=False, nullable=True)
    hidden = Column(INTEGER(), autoincrement=False, nullable=True)
    deleted_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    users_FK = relationship("User", back_populates="role_FK")
    # PrimaryKeyConstraint("id", name="roles_pkey"),
    # UniqueConstraint("uuid", name="roles_uuid_key"),

    permission = relationship("Permission", secondary=role_permission_rel, back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = Column("uuid", UUID(as_uuid=True), autoincrement=False, nullable=True)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)
    name = Column(VARCHAR(length=100), autoincrement=False, nullable=True)
    title = Column(VARCHAR(length=100), autoincrement=False, nullable=True)
    description = Column(VARCHAR(length=100), autoincrement=False, nullable=True)
    deleted_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    # PrimaryKeyConstraint("id", name="permissions_pkey"),
    # UniqueConstraint("uuid", name="permissions_uuid_key"),

    role = relationship("Role", secondary=role_permission_rel, back_populates="permission")


class User(Base):
    __tablename__ = "users"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)
    password = Column(VARCHAR(length=256), autoincrement=False, nullable=False)
    email = Column(VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    phone = Column(VARCHAR(length=16), autoincrement=False, nullable=True, unique=True)
    first_name = Column(VARCHAR(length=100), autoincrement=False, nullable=True)
    last_name = Column(VARCHAR(length=100), autoincrement=False, nullable=True)
    auth_token = Column(VARCHAR(length=128), autoincrement=False, nullable=True, unique=True)
    auth_token_valid_to = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    is_active = Column(BOOLEAN(), autoincrement=False, nullable=False)
    is_verified = Column(BOOLEAN(), autoincrement=False, nullable=False)
    service_token = Column("service_token", VARCHAR(length=100), autoincrement=False, nullable=True, unique=True)
    service_token_valid_to = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    tz = Column(VARCHAR(length=64), autoincrement=False, nullable=False)
    lang = Column(VARCHAR(length=8), autoincrement=False, nullable=False)
    user_role_id = Column(INTEGER(), ForeignKey("roles.id"), autoincrement=False, nullable=True)
    tos = Column(BOOLEAN(), autoincrement=False, nullable=True)
    deleted_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    role_FK = relationship("Role", back_populates="users_FK")
    # child_id = Column(Integer, ForeignKey("child.id"))
    # child = relationship("Child", back_populates="parents")

    # ForeignKeyConstraint(["user_role_id"], ["roles.id"], name="role_FK"),
    # PrimaryKeyConstraint("id", name="users_pkey"),
    # UniqueConstraint("email", name="users_email_key"),
    # UniqueConstraint("phone", name="users_phone_key"),


class Setting(Base):
    __tablename__ = "settings"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)
    entity = Column(VARCHAR(length=64), autoincrement=False, nullable=True)
    value = Column(VARCHAR(length=64), autoincrement=False, nullable=True)
    value_type = Column(VARCHAR(length=64), autoincrement=False, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)


class IdeaVote(Base):
    __tablename__ = "ideas_votes"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)
    idea_id = Column(INTEGER(), autoincrement=False, nullable=True)
    user_id = Column(INTEGER(), autoincrement=False, nullable=True)
    vote = Column(VARCHAR(length=16), autoincrement=False, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    # PrimaryKeyConstraint("id", name="ideas_votes_pkey"),


role_permission_rel = Table(
    "task_events_link",
    Base.metadata,
    Column("task_id", INTEGER(), autoincrement=False, nullable=False),
    Column("event_id", INTEGER(), autoincrement=False, nullable=False),
    # ForeignKeyConstraint(["event_id"], ["events.id"], name="task_events_link_fk_1"),
    # ForeignKeyConstraint(["task_id"], ["tasks.id"], name="task_events_link_fk"),
    # PrimaryKeyConstraint("task_id", "event_id", name="task_events_link_pkey"),
)

idea_file_rel = Table(
    "ideas_files_link",
    Base.metadata,
    Column("idea_id", ForeignKey("ideas.id"), autoincrement=False, nullable=False, primary_key=True),
    Column("file_id", ForeignKey("files.id"), autoincrement=False, nullable=False, primary_key=True),
    # ForeignKeyConstraint(["file_id"], ["files.id"], name="ideas_files_link_fk_1"),
    # ForeignKeyConstraint(["idea_id"], ["ideas.id"], name="ideas_files_link_fk"),
    # PrimaryKeyConstraint("idea_id", "file_id", name="ideas_files_link_pkey"),
)


class Idea(Base):
    __tablename__ = "ideas"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)
    author_id = Column(INTEGER(), autoincrement=False, nullable=True)
    upvotes = Column(INTEGER(), default=0, autoincrement=False, nullable=True)
    downvotes = Column(INTEGER(), default=0, autoincrement=False, nullable=True)
    title = Column(VARCHAR(length=256), autoincrement=False, nullable=True)
    description = Column(TEXT(), autoincrement=False, nullable=True)
    color = Column(VARCHAR(length=8), autoincrement=False, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    deleted_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    status = Column(VARCHAR(length=32), autoincrement=False, nullable=True)

    pictures = relationship("File", secondary=idea_file_rel, back_populates="idea")
    # PrimaryKeyConstraint("id", name="ideas_pkey"),
    # UniqueConstraint("uuid", name="ideas_uuid_key"),


class File(Base):
    __tablename__ = "files"
    id = Column(INTEGER(), Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    account_id = Column(INTEGER(), autoincrement=False, nullable=True)
    owner_id = Column(INTEGER(), autoincrement=False, nullable=True)
    file_name = Column(VARCHAR(length=256), autoincrement=False, nullable=True)
    extension = Column(VARCHAR(length=8), autoincrement=False, nullable=True)
    mimetype = Column(VARCHAR(length=256), autoincrement=False, nullable=True)
    size = Column(INTEGER(), autoincrement=False, nullable=True)
    deleted_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    # PrimaryKeyConstraint("id", name="files_pkey"),

    idea = relationship("Idea", secondary=idea_file_rel, back_populates="pictures")
