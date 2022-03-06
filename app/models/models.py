import uuid as uuid
from datetime import datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import EmailStr, HttpUrl, Json
from sqlmodel import Field, Relationship, SQLModel


class StandardResponse(SQLModel):  # OK
    ok: bool


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


class Users(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int
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
    # user_role_id: int = Field(default=None, foreign_key="roles.id")
    # user_info_id: Optional[int] = Field(default=None, foreign_key="users_info.id")
    tz: str
    lang: str
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    uuid: uuid.UUID

    usr_FK: List["Tasks"] = Relationship(back_populates="assignee")


class UserCreateIn(SQLModel):  # OK
    email: EmailStr
    password: Optional[str]
    password_confirmation: Optional[str]
    first_name: str
    last_name: str
    user_role_uuid: Optional[uuid.UUID]
    # details: Optional[UsersDetailsCreate]


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
    # role_FK: RolesWithPermissionsReturn


class UserSetPassIn(SQLModel):  # OK
    token: str
    password: str
    password_confirmation: str


class UserIndexResponse(SQLModel):
    first_name: str
    last_name: str
    uuid: uuid.UUID


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


class Tasks(SQLModel, table=True):
    __tablename__ = "tasks"
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: uuid.UUID
    client_id: int
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
    priority: str
    type: str
    all_day: bool
    recurring: bool
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
    client_id: int
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
    client_id: int
    owner_id: int
    file_name: str
    extension: str
    mimetype: str
    size: int
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    task: List[Tasks] = Relationship(back_populates="file", link_model=TaskFileLink)


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
    url: HttpUrl

    # task: List[TaskBasicInfo]


class TaskIndexResponse(SQLModel):
    uuid: uuid.UUID
    # author_id: int
    # assignee_id: Optional[int]
    title: str
    description: str
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    duration: Optional[int]
    is_active: Optional[bool]
    priority: str
    type: str
    assignee: Optional[UserIndexResponse]
    events: Optional[List[EventsBasicInfo]]


class FileBasicInfo(SQLModel):
    file_name: str
    extension: str
    mimetype: str
    size: int


class TaskSingleResponse(SQLModel):
    uuid: uuid.UUID
    # author_id: int
    # assignee_id: Optional[int]
    title: str
    description: str
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    duration: Optional[int]
    is_active: Optional[bool]
    priority: str
    type: str
    assignee: Optional[UserIndexResponse]
    file: Optional[List[FileBasicInfo]]
    event: Optional[EventsBasicInfo]


class TaskAddIn(SQLModel):
    title: str
    description: str
    assignee: Optional[uuid.UUID]
    priority: Optional[str]
    type: str  # single / planned / reccuring
    # planned:
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    all_day: bool
    # recurring:
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

    # connected_tasks: int


class TaskEditIn(SQLModel):
    # author_id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    priority: Optional[str]
    type: Optional[str]
    connected_tasks: Optional[int]
