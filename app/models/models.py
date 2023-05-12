import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db import Base

role_permission_rel = sa.Table(
    "roles_permissions_link",
    Base.metadata,
    sa.Column("role_id", sa.ForeignKey("roles.id"), autoincrement=False, nullable=False, primary_key=True),
    sa.Column("permission_id", sa.ForeignKey("permissions.id"), autoincrement=False, nullable=False, primary_key=True),
)

users_groups_rel = sa.Table(
    "users_groups_link",
    Base.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), autoincrement=False, nullable=False, primary_key=True),
    sa.Column("user_group_id", sa.ForeignKey("users_groups.id"), autoincrement=False, nullable=False, primary_key=True),
)

users_issues_rel = sa.Table(
    "users_issues_link",
    Base.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), autoincrement=False, nullable=False, primary_key=True),
    sa.Column("issue_id", sa.ForeignKey("issues.id"), autoincrement=False, nullable=False, primary_key=True),
)

users_items_rel = sa.Table(
    "users_items_link",
    Base.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), autoincrement=False, nullable=False, primary_key=True),
    sa.Column("item_id", sa.ForeignKey("items.id"), autoincrement=False, nullable=False, primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    role_name = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    role_title = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    role_description = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    is_custom = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    is_visible = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    is_system = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    users_FK = relationship("User", back_populates="role_FK")
    permission = relationship("Permission", secondary=role_permission_rel, back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    name = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    title = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    description = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    is_visible = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=False)
    group = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)

    # PrimaryKeyConstraint("id", name="permissions_pkey"),
    # UniqueConstraint("uuid", name="permissions_uuid_key"),

    role = relationship("Role", secondary=role_permission_rel, back_populates="permission")


class User(Base):
    __tablename__ = "users"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    email = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    phone = sa.Column(sa.VARCHAR(length=16), autoincrement=False, nullable=True, unique=True)
    password = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    first_name = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    last_name = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    auth_token = sa.Column(sa.VARCHAR(length=128), autoincrement=False, nullable=True, unique=True)
    auth_token_valid_to = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    user_role_id = sa.Column(sa.INTEGER(), sa.ForeignKey("roles.id"), autoincrement=False, nullable=True)
    is_active = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    is_verified = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    tos = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    tz = sa.Column(sa.VARCHAR(length=64), autoincrement=False, nullable=True, unique=True)
    lang = sa.Column(sa.VARCHAR(length=8), autoincrement=False, nullable=True, unique=True)
    tenant_id = sa.Column(sa.VARCHAR(length=64), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    deleted_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

    role_FK = relationship("Role", back_populates="users_FK")
    user_group = relationship("UserGroup", secondary=users_groups_rel, back_populates="users")
    problem = relationship("Issue", secondary=users_issues_rel, back_populates="users_issue")
    item = relationship("Item", secondary=users_items_rel, back_populates="users_item")


# file_idea_rel = sa.Table(
#     "files_ideas_link",
#     Base.metadata,
#     sa.Column("idea_id", sa.ForeignKey("ideas.id"), autoincrement=False, nullable=False, primary_key=True),
#     sa.Column("file_id", sa.ForeignKey("files.id"), autoincrement=False, nullable=False, primary_key=True),
#     # ForeignKeyConstraint(["file_id"], ["files.id"], name="files_ideas_link_fk_1"),
#     # ForeignKeyConstraint(["idea_id"], ["ideas.id"], name="files_ideas_link_fk"),
#     # PrimaryKeyConstraint("idea_id", "file_id", name="files_ideas_link_pkey"),
# )


# class Idea(Base):
#     __tablename__ = "ideas"
#     id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
#     uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
#     author_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
#     upvotes = sa.Column(sa.INTEGER(), default=0, autoincrement=False, nullable=True)
#     downvotes = sa.Column(sa.INTEGER(), default=0, autoincrement=False, nullable=True)
#     name = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
#     summary = sa.Column(sa.TEXT(), autoincrement=False, nullable=True)
#     text = sa.Column(sa.TEXT, autoincrement=False, nullable=True)
#     text_json = sa.Column(JSONB, autoincrement=False, nullable=True)
#     color = sa.Column(sa.VARCHAR(length=8), autoincrement=False, nullable=True)
#     status = sa.Column(sa.VARCHAR(length=32), autoincrement=False, nullable=True)
#     created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
#     updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
#     deleted_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

#     files_idea = relationship("File", secondary=file_idea_rel, back_populates="idea")


file_item_rel = sa.Table(
    "files_items_link",
    Base.metadata,
    sa.Column("item_id", sa.ForeignKey("items.id"), autoincrement=False, nullable=False, primary_key=True),
    sa.Column("file_id", sa.ForeignKey("files.id"), autoincrement=False, nullable=False, primary_key=True),
)


item_guide_rel = sa.Table(
    "items_guides_link",
    Base.metadata,
    sa.Column("item_id", sa.ForeignKey("items.id"), autoincrement=False, nullable=False, primary_key=True),
    sa.Column("guide_id", sa.ForeignKey("guides.id"), autoincrement=False, nullable=False, primary_key=True),
)


class Item(Base):
    __tablename__ = "items"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    author_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    symbol = sa.Column(sa.VARCHAR(length=32), autoincrement=False, nullable=True, unique=True)
    name = sa.Column(sa.VARCHAR(length=512), autoincrement=False, nullable=True)
    summary = sa.Column(sa.VARCHAR(length=1024), autoincrement=False, nullable=True)
    text = sa.Column(sa.TEXT(), autoincrement=False, nullable=True)
    text_json = sa.Column(JSONB, autoincrement=False, nullable=True)
    qr_code_id = sa.Column(sa.INTEGER, sa.ForeignKey("qr_codes.id"), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    # deleted_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

    files_item = relationship("File", secondary=file_item_rel, back_populates="item")
    item_guides = relationship("Guide", secondary=item_guide_rel, back_populates="item")
    users_item = relationship("User", secondary=users_items_rel, back_populates="item")

    qr_code = relationship("QrCode", back_populates="items_FK")
    issue_FK = relationship("Issue", back_populates="item")


file_guide_rel = sa.Table(
    "files_guides_link",
    Base.metadata,
    sa.Column("guide_id", sa.ForeignKey("guides.id"), autoincrement=False, nullable=False, primary_key=True),
    sa.Column("file_id", sa.ForeignKey("files.id"), autoincrement=False, nullable=False, primary_key=True),
    # ForeignKeyConstraint(["file_id"], ["files.id"], name="files_ideas_link_fk_1"),
    # ForeignKeyConstraint(["idea_id"], ["ideas.id"], name="files_ideas_link_fk"),
    # PrimaryKeyConstraint("idea_id", "file_id", name="files_ideas_link_pkey"),
)


class Guide(Base):
    __tablename__ = "guides"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    author_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    name = sa.Column("name", sa.VARCHAR(length=256), unique=False, autoincrement=False, nullable=False)
    text = sa.Column(sa.TEXT, autoincrement=False, nullable=True)
    text_json = sa.Column(JSONB, autoincrement=False, nullable=True)
    type = sa.Column(sa.VARCHAR(length=32), unique=False, autoincrement=False, nullable=True),
    is_public = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True),
    created_at = sa.Column("created_at", sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column("updated_at", sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

    files_guide = relationship("File", secondary=file_guide_rel, back_populates="guide")
    item = relationship("Item", secondary=item_guide_rel, back_populates="item_guides")


file_issue_rel = sa.Table(
    "files_issues_link",
    Base.metadata,
    sa.Column("issue_id", sa.ForeignKey("issues.id"), autoincrement=False, nullable=False, primary_key=True),
    sa.Column("file_id", sa.ForeignKey("files.id"), autoincrement=False, nullable=False, primary_key=True),
)

tag_issue_rel = sa.Table(
    "tags_issues_link",
    Base.metadata,
    sa.Column("issue_id", sa.ForeignKey("issues.id"), autoincrement=False, nullable=False, primary_key=True),
    sa.Column("tag_id", sa.ForeignKey("tags.id"), autoincrement=False, nullable=False, primary_key=True),
)

# part_used_issue_rel = sa.Table(
#     "parts_used_issues_link",
#     Base.metadata,
#     sa.Column("issue_id", sa.ForeignKey("issues.id"), autoincrement=False, nullable=False, primary_key=True),
#     sa.Column("part_used_id", sa.ForeignKey("parts_used.id"), autoincrement=False, nullable=False, primary_key=True),
# )


class Issue(Base):
    __tablename__ = "issues"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    author_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    author_name = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    item_id = sa.Column(sa.INTEGER(), sa.ForeignKey("items.id"), autoincrement=False, nullable=True)
    symbol = sa.Column(sa.VARCHAR(length=32), autoincrement=False, nullable=True, unique=True)
    name = sa.Column(sa.VARCHAR(length=512), autoincrement=False, nullable=True)
    summary = sa.Column(sa.VARCHAR(length=1024), autoincrement=False, nullable=True)
    text = sa.Column(sa.TEXT(), autoincrement=False, nullable=True)
    text_json = sa.Column(JSONB, autoincrement=False, nullable=True)
    color = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    priority = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    status = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    # qr_code_id = sa.Column(sa.INTEGER, sa.ForeignKey("qr_codes.id"), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    deleted_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

    files_issue = relationship("File", secondary=file_issue_rel, back_populates="issue")
    users_issue = relationship("User", secondary=users_issues_rel, back_populates="problem")
    tags_issue = relationship("Tag", secondary=tag_issue_rel, back_populates="tag")

    item = relationship("Item", back_populates="issue_FK")
    # part = relationship("PartUsed", secondary=part_used_issue_rel, back_populates="issue_part")


class PartUsed(Base):
    __tablename__ = "parts_used"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    item_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    issue_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    author_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    name = sa.Column(sa.VARCHAR(length=512), autoincrement=False, nullable=True)
    description = sa.Column(sa.VARCHAR(length=512), autoincrement=False, nullable=True)
    price = sa.Column(sa.DECIMAL(precision=10, scale=2), autoincrement=False, nullable=True)
    quantity = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    unit = sa.Column(sa.VARCHAR(length=32), autoincrement=False, nullable=True)
    value = sa.Column(sa.DECIMAL(precision=10, scale=2), autoincrement=False, nullable=True)
    description = sa.Column(sa.VARCHAR(length=512), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    deleted_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

    # issue_part = relationship("Issue", secondary=part_used_issue_rel, back_populates="part")


class File(Base):
    __tablename__ = "files"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    owner_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    file_name = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    file_description = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    extension = sa.Column(sa.VARCHAR(length=8), autoincrement=False, nullable=True)
    mimetype = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    size = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    deleted_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

    # idea = relationship("Idea", secondary=file_idea_rel, back_populates="files_idea")
    item = relationship("Item", secondary=file_item_rel, back_populates="files_item")
    guide = relationship("Guide", secondary=file_guide_rel, back_populates="files_guide")
    issue = relationship("Issue", secondary=file_issue_rel, back_populates="files_issue")


class Setting(Base):
    __tablename__ = "settings"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    name = sa.Column(sa.VARCHAR(length=256), unique=True, autoincrement=False, nullable=True)
    value = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    value_type = sa.Column(sa.VARCHAR(length=64), autoincrement=False, nullable=True)
    prev_value = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    descripton = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)


class SettingUser(Base):
    __tablename__ = "settings_users"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    user_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    name = sa.Column(sa.VARCHAR(length=256), unique=True, autoincrement=False, nullable=True)
    value = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    value_type = sa.Column(sa.VARCHAR(length=64), autoincrement=False, nullable=True)
    prev_value = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)


class SettingNotification(Base):
    __tablename__ = "settings_notifications"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    user_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    user_uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    sms_notification_level = sa.Column(sa.VARCHAR(length=128), autoincrement=False, nullable=True)
    email_notification_level = sa.Column(sa.VARCHAR(length=128), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)


class QrCode(Base):
    __tablename__ = "qr_codes"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    resource = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    qr_code_id = sa.Column(sa.VARCHAR(length=512), autoincrement=False, nullable=True)
    qr_code_full_id = sa.Column(sa.VARCHAR(length=512), autoincrement=False, nullable=True)
    ecc = sa.Column(sa.CHAR(length=1), autoincrement=False, nullable=True)
    resource_uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    public_access = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

    items_FK = relationship("Item", back_populates="qr_code")


class UserGroup(Base):
    __tablename__ = "users_groups"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    name = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True)
    description = sa.Column(sa.VARCHAR(length=512), autoincrement=False, nullable=True)
    symbol = sa.Column(sa.VARCHAR(length=64), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    # users_FK = relationship("User", back_populates="role_FK")
    # permission = relationship("Permission", secondary=role_permission_rel, back_populates="role")

    users = relationship("User", secondary=users_groups_rel, back_populates="user_group")  # Roles


class Event(Base):
    __tablename__ = "events"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    action = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    # title = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    description = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    internal_value = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    resource = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    resource_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    resource_uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    author_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    author_uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    author_name = sa.Column(sa.VARCHAR(length=256), unique=True, autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)


class EventSummary(Base):
    __tablename__ = "events_summary"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    resource = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    resource_uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    # issue_uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    action = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    date_from = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    date_to = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    duration = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    internal_value = sa.Column(sa.VARCHAR(length=512), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)


class Tag(Base):
    __tablename__ = "tags"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    name = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    color = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    icon = sa.Column(sa.VARCHAR(length=512), unique=True, autoincrement=False, nullable=True)
    author_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    is_hidden = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    deleted_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

    tag = relationship("Issue", secondary=tag_issue_rel, back_populates="tags_issue")
