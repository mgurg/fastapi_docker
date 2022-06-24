import uuid as uuid
from datetime import datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from faker import Faker
from pydantic import EmailStr, HttpUrl, Json
from pydantic_factories import ModelFactory, Use
from sqlmodel import Field, Relationship, SQLModel

from app.service.helpers import get_uuid


class StandardResponse(SQLModel):  # OK
    ok: bool


class Settings(SQLModel, table=True):
    __tablename__ = "settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int
    entity: str
    value: str
    value_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=False)
    updated_at: Optional[datetime]


class SettingAddIn(SQLModel):
    entity: str
    value: str
    value_type: str


class TasksLog(SQLModel, table=True):
    __tablename__ = "tasks_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int
    uuid: uuid.UUID
    user_id: int
    start_at: datetime
    end_at: Optional[datetime]
    duration: Optional[int]
    from_value: str
    to_value: str
    action_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=False)


class TasksLogIn(SQLModel):
    to_value: Optional[str]
    action_type: str


class LoginHistory(SQLModel, table=True):
    __tablename__ = "login_history"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int]
    login_date: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    os: Optional[str]
    browser: Optional[str]
    browser_lang: Optional[str]
    ipinfo: Optional[str]
    ip_address: Optional[str]
    failed_login: Optional[str]
    failed_passwd: Optional[str]


# class UsersOrg(SQLModel, table=True):
#     __tablename__ = "users_organisation"
#     id: Optional[int] = Field(default=None, primary_key=True)
#     uuid: Optional[str]
#     name: Optional[str]
#     description: Optional[str]
#     phone_1: Optional[str]
#     phone_1_name: Optional[str]
#     phone_2: Optional[str]
#     phone_2_name: Optional[str]
#     phone_3: Optional[str]
#     phone_3_name: Optional[str]
#     email_1: Optional[str]
#     email_2: Optional[str]
#     email_3: Optional[str]
#     id_address_1: Optional[str]
#     id_address_2: Optional[str]
#     id_address_3: Optional[str]
#     nip: Optional[str]
#     regon: Optional[str]
#     created_at: Optional[str]
#     updated_a: Optional[str]


class Accounts(SQLModel, table=True):
    __tablename__ = "accounts"
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: uuid.UUID
    account_id: int
    company: str
    registered_at: Optional[datetime]
    paid_period_from: Optional[datetime]
    current_period_ends: Optional[datetime]
    plan: Optional[str]
    nip: Optional[str]
    address: Optional[str]
    company_id: Optional[str]
    ideas_id: Optional[str]


class RolePermissionLink(SQLModel, table=True):
    __tablename__ = "roles_permissions_link"
    role_id: Optional[int] = Field(default=None, foreign_key="roles.id", primary_key=True)
    permission_id: Optional[int] = Field(default=None, foreign_key="permissions.id", primary_key=True)


class Roles(SQLModel, table=True):
    __tablename__ = "roles"
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: uuid.UUID
    account_id: int
    role_name: str
    role_description: str
    hidden: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    permission: List["Permissions"] = Relationship(back_populates="role", link_model=RolePermissionLink)  # hasMany
    users_FK: List["Users"] = Relationship(back_populates="role_FK")  # hasOne


class Permissions(SQLModel, table=True):
    __tablename__ = "permissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: uuid.UUID
    name: str
    title: str
    description: str
    role: List[Roles] = Relationship(back_populates="permission", link_model=RolePermissionLink)


class PermissionsMini(SQLModel):
    name: str


class RolesWithPermissionsReturn(SQLModel):  # OK
    role_name: Optional[str]
    # role_description: Optional[str]
    # desc: str
    # uuid: uuid.UUID
    permission: List[PermissionsMini]


class Users(SQLModel, table=True):
    __tablename__ = "users"
    # __table_args__ = {"schema": "public", "keep_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int
    password: str
    email: Optional[EmailStr] = Field(sa_column_kwargs={"unique": True})
    phone: Optional[str] = Field(sa_column_kwargs={"unique": True})
    first_name: Optional[str]
    last_name: Optional[str]
    auth_token: Optional[str]
    auth_token_valid_to: Optional[datetime]
    is_active: bool
    service_token: Optional[str]
    service_token_valid_to: Optional[datetime]
    user_role_id: int = Field(default=None, foreign_key="roles.id")
    # user_info_id: Optional[int] = Field(default=None, foreign_key="users_info.id")
    tz: str
    lang: str
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    uuid: uuid.UUID

    usr_FK: List["Tasks"] = Relationship(back_populates="assignee")
    role_FK: Optional["Roles"] = Relationship(back_populates="users_FK")  # hasOne


class UserCreateIn(SQLModel):  # OK
    email: EmailStr
    password: Optional[str]
    password_confirmation: Optional[str]
    phone: Optional[str]
    first_name: str
    last_name: str
    user_role_uuid: Optional[uuid.UUID]
    # details: Optional[UsersDetailsCreate]


class UserCreateIn(SQLModel):  # OK
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    password: Optional[str]
    password_confirmation: Optional[str]
    user_role_uuid: Optional[uuid.UUID]


class UserRegisterIn(SQLModel):  # OK
    email: EmailStr
    password: str
    password_confirmation: str
    tos: bool
    tz: Optional[str]
    lang: Optional[str]


class UserActivateOut(SQLModel):  # OK
    email: EmailStr


class UserFirstRunIn(SQLModel):  # OK
    first_name: str
    last_name: str
    nip: str
    token: str


class UserLoginIn(SQLModel):  # OK
    email: EmailStr
    password: Optional[str]
    permanent: bool


class UserLoginOut(SQLModel):  # OK
    auth_token: str
    first_name: str
    last_name: str
    tz: str
    lang: str
    uuid: uuid.UUID
    role_FK: RolesWithPermissionsReturn


class UserSetPassIn(SQLModel):  # OK
    token: str
    password: str
    password_confirmation: str


class UserIndexResponse(SQLModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    uuid: uuid.UUID
    is_active: bool
    # role_FK: RolesWithPermissionsReturn


class TaskIdeaLink(SQLModel, table=True):
    __tablename__ = "ideas_files_link"
    idea_id: Optional[int] = Field(default=None, foreign_key="ideas.id", primary_key=True)
    file_id: Optional[int] = Field(default=None, foreign_key="files.id", primary_key=True)


class TaskFileLink(SQLModel, table=True):
    __tablename__ = "task_files_link"
    task_id: Optional[int] = Field(default=None, foreign_key="tasks.id", primary_key=True)
    file_id: Optional[int] = Field(default=None, foreign_key="files.id", primary_key=True)


class TaskEventLink(SQLModel, table=True):
    __tablename__ = "task_events_link"
    task_id: Optional[int] = Field(default=None, foreign_key="tasks.id", primary_key=True)
    event_id: Optional[int] = Field(default=None, foreign_key="events.id", primary_key=True)


class EventsBasicInfo(SQLModel):
    uuid: Optional[uuid.UUID]


class Ideas(SQLModel, table=True):
    __tablename__ = "ideas"
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: uuid.UUID
    account_id: int
    author_id: Optional[int]
    color: str
    title: str
    description: str
    upvotes: Optional[int]
    downvotes: Optional[int]
    status: Optional[str]
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    pictures: Optional[List["Files"]] = Relationship(back_populates="idea", link_model=TaskIdeaLink)


class IdeasVotes(SQLModel, table=True):
    __tablename__ = "ideas_votes"
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: uuid.UUID
    account_id: int
    idea_id: int
    user_id: int
    vote: str
    created_at: datetime


class IdeasVotesIn(SQLModel):
    idea_uuid: uuid.UUID
    vote: str


class Tasks(SQLModel, table=True):
    __tablename__ = "tasks"
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: uuid.UUID
    account_id: int
    author_id: Optional[int]
    title: str
    description: str
    color: str
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    time_from: Optional[time]
    time_to: Optional[time]
    duration: Optional[int]
    is_active: Optional[bool]
    priority: Optional[str]
    mode: Optional[str]
    all_day: Optional[bool]
    recurring: bool
    status: Optional[str]
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    assignee_id: Optional[int] = Field(default=None, foreign_key="users.id")
    assignee: Optional[Users] = Relationship(back_populates="usr_FK")

    file: List["Files"] = Relationship(back_populates="task", link_model=TaskFileLink)

    events: List["Events"] = Relationship(back_populates="tasks", link_model=TaskEventLink)

    # sa_relationship_kwargs={
    #     "primaryjoin": "Events.id==TaskEventLink.event_id",
    #     "secondaryjoin": "TaskEventLink.task_id==Tasks.id",
    # },

    # event_id: Optional[int] = Field(default=None, foreign_key="events.id")
    # event: Optional[Events] = Relationship(back_populates="event_FK")

    # TODO: Full text search
    # https://github.com/jorzel/postgres-full-text-search?ref=pythonawesome.com
    # https://www.compose.com/articles/mastering-postgresql-tools-full-text-search-and-phrase-search/


class Events(SQLModel, table=True):
    __tablename__ = "events"
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: uuid.UUID
    account_id: int
    recurring: bool
    freq: str
    interval: int
    date_from: datetime
    date_to: datetime
    occurrence_number: Optional[int]
    all_day: bool
    recurring: bool
    time_from: Optional[time]
    time_to: Optional[time]
    duration: Optional[int]
    at_mo: bool
    at_tu: bool
    at_we: bool
    at_th: bool
    at_fr: bool
    at_sa: bool
    at_su: bool

    # event_FK: List["Tasks"] = Relationship(back_populates="event")
    tasks: List[Tasks] = Relationship(back_populates="events", link_model=TaskEventLink)


class Files(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: uuid.UUID
    account_id: int
    owner_id: int
    file_name: str
    extension: str
    mimetype: str
    size: int
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    task: List[Tasks] = Relationship(back_populates="file", link_model=TaskFileLink)
    idea: List[Ideas] = Relationship(back_populates="pictures", link_model=TaskIdeaLink)


class TaskBasicInfo(SQLModel):
    title: str


class FileResponse(SQLModel):
    uuid: uuid.UUID
    file_name: str
    extension: str
    mimetype: str
    size: int

    # task: List[TaskBasicInfo]


class FileUrlResponse(SQLModel):
    uuid: uuid.UUID
    file_name: str
    extension: str
    mimetype: str
    size: int
    # url: HttpUrl

    # task: List[TaskBasicInfo]


class TaskIndexResponse(SQLModel):
    uuid: uuid.UUID
    color: str
    status: Optional[str]
    # author_id: int
    # assignee_id: Optional[int]
    title: str
    description: str
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    duration: Optional[int]
    is_active: Optional[bool]
    priority: str
    assignee: Optional[UserIndexResponse]
    events: Optional[List[EventsBasicInfo]]
    created_at: datetime


class FileBasicInfo(SQLModel):
    uuid: uuid.UUID
    file_name: str
    extension: str
    mimetype: str
    size: int


class IdeaIndexResponse(SQLModel):
    uuid: uuid.UUID
    color: str
    title: str
    description: str
    upvotes: Optional[int]
    downvotes: Optional[int]
    status: Optional[str]
    created_at: datetime
    pictures: Optional[List[FileBasicInfo]]


class IdeaAddIn(SQLModel):
    title: str
    description: str
    color: str = "green"
    files: Optional[List[uuid.UUID]]


class IdeaEditIn(SQLModel):
    title: Optional[str]
    description: Optional[str]
    color: Optional[str]
    status: Optional[str]
    vote: Optional[str]
    files: Optional[List[uuid.UUID]]


class TaskSingleResponse(SQLModel):
    uuid: uuid.UUID
    color: str
    status: Optional[str]
    # author_id: int
    # assignee_id: Optional[int]
    title: str
    description: str
    mode: Optional[str]
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    all_day: Optional[bool]
    duration: Optional[int]
    is_active: Optional[bool]
    assignee: Optional[UserIndexResponse]
    file: Optional[List[FileBasicInfo]]
    event: Optional[EventsBasicInfo]
    created_at: datetime


class TaskAddIn(SQLModel):
    title: str
    description: str
    assignee: Optional[uuid.UUID]
    priority: Optional[str]
    mode: Optional[str]  # single / planned / reccuring
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    all_day: Optional[bool]
    recurring: bool
    interval: Optional[int]
    freq: Optional[str] = "DAILY"
    at_Mo: Optional[bool]
    at_Tu: Optional[bool]
    at_We: Optional[bool]
    at_Th: Optional[bool]
    at_Fr: Optional[bool]
    at_Sa: Optional[bool]
    at_Su: Optional[bool]
    color: str = "green"
    files: Optional[List[uuid.UUID]]


class TaskEditIn(SQLModel):
    # author_id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    assignee: Optional[uuid.UUID]
    priority: Optional[str]
    mode: Optional[str]
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    all_day: Optional[bool]
    recurring: Optional[bool]
    interval: Optional[int]
    freq: Optional[str]
    at_Mo: Optional[bool]
    at_Tu: Optional[bool]
    at_We: Optional[bool]
    at_Th: Optional[bool]
    at_Fr: Optional[bool]
    at_Sa: Optional[bool]
    at_Su: Optional[bool]
    color: Optional[str]
    files: Optional[List[uuid.UUID]]


class TaskCreateFactory(ModelFactory):
    __model__ = Tasks
    uuid = get_uuid()
    account_id = 2
    author_id: 2
    title = Use(Faker().name)
    description = Use(Faker().name)
    priority = Use(Faker().name)
    type = Use(Faker().name)
    color = Use(Faker().safe_color_name)
    recurring = Use(Faker().boolean)

    # date_from: Optional[datetime]
    # date_to: Optional[datetime]
    # time_from: Optional[time]
    # time_to: Optional[time]
    # duration: Optional[int]
    # is_active: Optional[bool]
    # priority: Optional[str]
    # type: Optional[str]
    # all_day: Optional[bool]
    # recurring: bool
    # deleted_at: Optional[datetime]
    # created_at: datetime
    # updated_at: Optional[datetime]

    # name = Use(Faker().name)
    # degree = None
    # age = None
    # student_id = None
    # date = None
    # wallet_id = None
    # alias = None
    # invitation_state = None
    # connection_id = None

    #     created_at: datetime.datetime = Field(
    #     default_factory=datetime.datetime.utcnow, index=False
    # )
