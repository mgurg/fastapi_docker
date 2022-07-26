from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class Accounts(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="accounts_pkey"),
        UniqueConstraint("uuid", name="accounts_uuid_key"),
    )

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    company = Column(String(256))
    registered_at = Column(DateTime(True))
    paid_period_from = Column(DateTime(True))
    current_period_ends = Column(DateTime(True))
    plan = Column(String(32))
    nip = Column(String(32))
    address = Column(String)
    company_id = Column(String(8))
    ideas_id = Column(String(8))
    account_id = Column(Integer)


class Comments(Base):
    __tablename__ = "comments"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="comments_pkey"),
        UniqueConstraint("uuid", name="comments_uuid_key"),
    )

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    message = Column(String(1024))
    user_id = Column(Integer)

    task = relationship("Tasks", secondary="task_comments_link", back_populates="comment")


class Events(Base):
    __tablename__ = "events"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="events_pkey"),
        UniqueConstraint("uuid", name="events_uuid_key"),
    )

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    account_id = Column(Integer)
    recurring = Column(Boolean)
    interval = Column(Integer)
    freq = Column(String(8))
    at_mo = Column(Boolean)
    at_tu = Column(Boolean)
    at_we = Column(Boolean)
    at_th = Column(Boolean)
    at_fr = Column(Boolean)
    at_sa = Column(Boolean)
    at_su = Column(Boolean)
    date_from = Column(DateTime(True))
    all_day = Column(Boolean)
    date_to = Column(DateTime(True))
    occurrence_number = Column(Integer)
    time_from = Column(Time(True))
    time_to = Column(Time)
    duration = Column(Integer)

    task = relationship("Tasks", secondary="task_events_link", back_populates="event")


class Files(Base):
    __tablename__ = "files"
    __table_args__ = (PrimaryKeyConstraint("id", name="files_pkey"),)

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    account_id = Column(Integer)
    owner_id = Column(Integer)
    file_name = Column(String(256))
    extension = Column(String(8))
    mimetype = Column(String(256))
    size = Column(Integer)
    deleted_at = Column(DateTime(True))
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))

    idea = relationship("Ideas", secondary="ideas_files_link", back_populates="file")
    task = relationship("Tasks", secondary="task_files_link", back_populates="file")


class Ideas(Base):
    __tablename__ = "ideas"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="ideas_pkey"),
        UniqueConstraint("uuid", name="ideas_uuid_key"),
    )

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    account_id = Column(Integer)
    author_id = Column(Integer)
    upvotes = Column(Integer, server_default=text("0"))
    downvotes = Column(Integer, server_default=text("0"))
    title = Column(String(256))
    description = Column(Text)
    color = Column(String(8))
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))
    deleted_at = Column(DateTime(True))
    status = Column(String(32))

    file = relationship("Files", secondary="ideas_files_link", back_populates="idea")


class IdeasVotes(Base):
    __tablename__ = "ideas_votes"
    __table_args__ = (PrimaryKeyConstraint("id", name="ideas_votes_pkey"),)

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    account_id = Column(Integer)
    idea_id = Column(Integer)
    user_id = Column(Integer)
    vote = Column(String(16))
    created_at = Column(DateTime(True))


class LoginHistory(Base):
    __tablename__ = "login_history"
    __table_args__ = (PrimaryKeyConstraint("id", name="login_history_pkey"),)

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    login_date = Column(DateTime(True), nullable=False)
    failed = Column(Boolean, nullable=False)
    account_id = Column(Integer)
    ip_address = Column(String(16))
    user_agent = Column(String(256))
    os = Column(String(32))
    browser = Column(String(32))
    browser_lang = Column(String(32))
    ipinfo = Column(JSON)
    failed_login = Column(String(256))
    failed_passwd = Column(String(256))


class Permissions(Base):
    __tablename__ = "permissions"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="permissions_pkey"),
        UniqueConstraint("uuid", name="permissions_uuid_key"),
    )

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    account_id = Column(Integer)
    name = Column(String(100))
    title = Column(String(100))
    description = Column(String(100))
    deleted_at = Column(DateTime(True))
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))

    role = relationship("Roles", secondary="roles_permissions_link", back_populates="permission")


class Roles(Base):
    __tablename__ = "roles"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="roles_pkey"),
        UniqueConstraint("uuid", name="roles_uuid_key"),
    )

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    account_id = Column(Integer)
    role_name = Column(String(100))
    role_description = Column(String(100))
    hidden = Column(Integer)
    deleted_at = Column(DateTime(True))
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))

    permission = relationship("Permissions", secondary="roles_permissions_link", back_populates="role")
    users = relationship("Users", back_populates="user_role")


class Settings(Base):
    __tablename__ = "settings"
    __table_args__ = (PrimaryKeyConstraint("id", name="settings_pkey"),)

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    account_id = Column(Integer)
    entity = Column(String(64))
    value = Column(String(64))
    value_type = Column(String(64))
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))


class TasksLog(Base):
    __tablename__ = "tasks_log"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="task_duration_pkey"),
        UniqueConstraint("uuid", name="task_duration_uuid_key"),
    )

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    created_at = Column(DateTime(True))
    start_at = Column(DateTime(True))
    end_at = Column(DateTime(True))
    duration = Column(Integer)
    from_value = Column(String(32))
    to_value = Column(String(32))
    user_id = Column(Integer)
    action_type = Column(String(32))
    user_name = Column(String(128))
    task_id = Column(Integer)


t_ideas_files_link = Table(
    "ideas_files_link",
    metadata,
    Column("idea_id", Integer, nullable=False),
    Column("file_id", Integer, nullable=False),
    ForeignKeyConstraint(["file_id"], ["files.id"], name="ideas_files_link_fk_1"),
    ForeignKeyConstraint(["idea_id"], ["ideas.id"], name="ideas_files_link_fk"),
    PrimaryKeyConstraint("idea_id", "file_id", name="ideas_files_link_pkey"),
)


t_roles_permissions_link = Table(
    "roles_permissions_link",
    metadata,
    Column("role_id", Integer, nullable=False),
    Column("permission_id", Integer, nullable=False),
    ForeignKeyConstraint(["permission_id"], ["permissions.id"], name="roles_permissions_link_fk_1"),
    ForeignKeyConstraint(["role_id"], ["roles.id"], name="roles_permissions_link_fk"),
    PrimaryKeyConstraint("role_id", "permission_id", name="roles_permissions_link_pkey"),
)


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        ForeignKeyConstraint(["user_role_id"], ["roles.id"], name="role_FK"),
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("email", name="users_email_key"),
        UniqueConstraint("phone", name="users_phone_key"),
    )

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    password = Column(String(256), nullable=False)
    is_active = Column(Boolean, nullable=False)
    tz = Column(String(64), nullable=False)
    lang = Column(String(8), nullable=False)
    is_verified = Column(Boolean, nullable=False)
    uuid = Column(UUID)
    account_id = Column(Integer)
    email = Column(String(256))
    phone = Column(String(16))
    first_name = Column(String(100))
    last_name = Column(String(100))
    auth_token = Column(String(128))
    auth_token_valid_to = Column(DateTime(True))
    service_token = Column(String(100))
    service_token_valid_to = Column(DateTime(True))
    user_role_id = Column(Integer)
    tos = Column(Boolean)
    deleted_at = Column(DateTime(True))
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))

    user_role = relationship("Roles", back_populates="users")
    tasks = relationship("Tasks", foreign_keys="[Tasks.assignee_id]", back_populates="assignee")
    tasks_ = relationship("Tasks", foreign_keys="[Tasks.author_id]", back_populates="author")


class Tasks(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        ForeignKeyConstraint(["assignee_id"], ["users.id"], name="tasks_assignee_fk"),
        ForeignKeyConstraint(["author_id"], ["users.id"], name="tasks_fk"),
        PrimaryKeyConstraint("id", name="tasks_pkey"),
    )

    id = Column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
    )
    uuid = Column(UUID)
    account_id = Column(Integer)
    author_id = Column(Integer)
    assignee_id = Column(Integer)
    title = Column(String(128))
    description = Column(String(256))
    date_from = Column(DateTime(True))
    date_to = Column(DateTime(True))
    duration = Column(Integer)
    is_active = Column(Boolean)
    priority = Column(String(128))
    mode = Column(String(8))
    deleted_at = Column(DateTime(True))
    created_at = Column(DateTime(True))
    updated_at = Column(DateTime(True))
    time_from = Column(Time(True))
    time_to = Column(Time(True))
    recurring = Column(Boolean)
    all_day = Column(Boolean)
    color = Column(String(8))
    started_at = Column(Time(True))
    status = Column(String(32))

    comment = relationship("Comments", secondary="task_comments_link", back_populates="task")
    event = relationship("Events", secondary="task_events_link", back_populates="task")
    file = relationship("Files", secondary="task_files_link", back_populates="task")
    assignee = relationship("Users", foreign_keys=[assignee_id], back_populates="tasks")
    author = relationship("Users", foreign_keys=[author_id], back_populates="tasks_")


t_task_comments_link = Table(
    "task_comments_link",
    metadata,
    Column("task_id", Integer, nullable=False),
    Column("comment_id", Integer, nullable=False),
    ForeignKeyConstraint(["comment_id"], ["comments.id"], name="task_comments_link_fk_1"),
    ForeignKeyConstraint(["task_id"], ["tasks.id"], name="task_comments_link_fk"),
    PrimaryKeyConstraint("task_id", "comment_id", name="task_comments_link_pkey"),
)


t_task_events_link = Table(
    "task_events_link",
    metadata,
    Column("task_id", Integer, nullable=False),
    Column("event_id", Integer, nullable=False),
    ForeignKeyConstraint(["event_id"], ["events.id"], name="task_events_link_fk_1"),
    ForeignKeyConstraint(["task_id"], ["tasks.id"], name="task_events_link_fk"),
    PrimaryKeyConstraint("task_id", "event_id", name="task_events_link_pkey"),
)


t_task_files_link = Table(
    "task_files_link",
    metadata,
    Column("task_id", Integer, nullable=False),
    Column("file_id", Integer, nullable=False),
    ForeignKeyConstraint(["file_id"], ["files.id"], name="task_files_link_fk_1"),
    ForeignKeyConstraint(["task_id"], ["tasks.id"], name="task_files_link_fk"),
    PrimaryKeyConstraint("task_id", "file_id", name="task_files_link_pkey"),
)
