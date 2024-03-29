import csv
import io
from collections import Counter
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.crud import crud_events, crud_files, crud_issues, crud_items, crud_settings, crud_tags, crud_users
from app.crud.crud_auth import get_public_company_from_tenant
from app.db import get_db
from app.models.models import User
from app.schemas.requests import IssueAddIn, IssueChangeStatus, IssueEditIn
from app.schemas.responses import EventTimelineResponse, IssueIndexResponse, IssueResponse, StandardResponse
from app.service import event
from app.service.bearer_auth import has_token
from app.service.helpers import is_valid_uuid
from app.service.notifications import notify_users
from app.storage.aws_s3 import generate_presigned_url

issue_router = APIRouter()

CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[Session, Depends(get_db)]


@issue_router.get("/", response_model=Page[IssueIndexResponse])
def issue_get_all(
    *,
    db: UserDB,
    params: Annotated[Params, Depends()],
    auth_user: CurrentUser,
    search: str | None = None,
    status: str = "active",
    user_uuid: UUID | None = None,
    priority: str | None = None,
    dateFrom: datetime | None = None,
    dateTo: datetime | None = None,
    tag: Annotated[list[UUID] | None, Query()] = None,
    field: str = "created_at",
    order: str = "asc",
):
    if field not in ["created_at", "name", "priority", "status"]:
        field = "created_at"

    tag_ids = None
    if tag is not None:
        tag_ids = crud_tags.get_tags_id_by_uuid(db, tag)

    user_id = None
    if user_uuid is not None:
        db_user = crud_users.get_user_by_uuid(db, user_uuid)
        if db_user is None:
            raise HTTPException(status_code=401, detail="User not found")
        user_id = db_user.id

    db_issues_query = crud_issues.get_issues(field, order, search, status, user_id, priority, dateFrom, dateTo, tag_ids)
    return paginate(db, db_issues_query)


@issue_router.get("/export")
def get_export_issues(*, db: UserDB, auth_user: CurrentUser):
    db_issues_query = crud_issues.get_issues("name", "asc", None, "all", None, None, None, None, None)
    result = db.execute(db_issues_query)  # await db.execute(query)

    db_issues = result.scalars().all()
    f = io.StringIO()
    csv_file = csv.writer(f, delimiter=";")
    csv_file.writerow(["Symbol", "Name", "Description", "Author", "Status", "Created at"])
    for u in db_issues:
        csv_file.writerow([u.symbol, u.name, u.text, u.author_name, u.status, u.created_at])

    f.seek(0)
    response = StreamingResponse(f, media_type="text/csv")
    filename = f"issues_{datetime.today().strftime('%Y-%m-%d')}.csv"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


@issue_router.get("/timeline/{issue_uuid}", response_model=list[EventTimelineResponse])
def item_get_timeline_history(
    *, db: UserDB, issue_uuid: UUID, auth_user: CurrentUser, thread_resource: str | None = None
):
    db_events = crud_events.get_events_by_thread(db, issue_uuid, "issue")
    if not db_events:
        raise HTTPException(status_code=400, detail="Event not found!")
    return db_events


@issue_router.get("/summary/{issue_uuid}")
def item_get_issue_summary(*, db: UserDB, issue_uuid: UUID, auth_user: CurrentUser):
    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)

    if not db_issue or db_issue.status != "done":
        raise HTTPException(status_code=400, detail="Issue not found!")

    events_info = crud_events.get_events_for_issue_summary(db, "issue", issue_uuid)

    events_dict_keys = ("action", "duration", "counter")
    events_info_dict = [dict(zip(events_dict_keys, values, strict=False)) for values in events_info]

    users_uuids = crud_events.get_basic_summary_users_uuids(db, "issue", db_issue.uuid, "issueUserActivity")

    events_users_info = crud_events.get_events_user_issue_summary(db, "issue", issue_uuid, users_uuids)

    events_users_info_keys = ("user_uuid", "duration", "counter")
    events_users_info_dict = [dict(zip(events_users_info_keys, values, strict=False)) for values in events_users_info]

    for user in events_users_info_dict:
        user_details = crud_users.get_user_by_uuid(db, user["user_uuid"])
        user["name"] = user_details.first_name + " " + user_details.last_name
        del user["user_uuid"]
        # events_users_info_dict

    result = {"events": events_info_dict, "users": events_users_info_dict}

    return result


@issue_router.get("/{issue_uuid}", response_model=IssueResponse)  # , response_model=Page[UserIndexResponse]
def issue_get_one(*, db: UserDB, issue_uuid: UUID, request: Request, auth_user: CurrentUser):
    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)

    if not db_issue:
        raise HTTPException(status_code=400, detail="Issue not found!")

    try:
        for picture in db_issue.files_issue:
            picture.url = generate_presigned_url(
                request.headers.get("tenant", "public"), "_".join([str(picture.uuid), picture.file_name])
            )
    except Exception as e:
        capture_exception(e)

    return db_issue


@issue_router.post("/", response_model=IssueResponse)  #
def issue_add(*, db: UserDB, request: Request, issue: IssueAddIn, auth_user: CurrentUser):
    tenant_id = request.headers.get("tenant", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Unknown Company!")

    get_public_company_from_tenant(tenant_id)

    files = []
    if issue.files is not None:
        for file in issue.files:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

    tags = []
    if issue.tags is not None:
        for tag in issue.tags:
            db_tag = crud_tags.get_tag_by_uuid(db, tag)
            if db_tag:
                tags.append(db_tag)

    issue_uuid = str(uuid4())

    db_user = crud_users.get_user_by_id(db, auth_user.id)

    db_item = crud_items.get_item_by_uuid(db, issue.item_uuid)
    item_id = None
    if db_item:
        item_id = db_item.id

    description = None
    if issue.text_html is not None:
        description = BeautifulSoup(issue.text_html, "html.parser").get_text()  # TODO add fix when empty

    last_issue_id = crud_issues.get_last_issue_id(db)
    if not last_issue_id:
        last_issue_id = 0
    last_issue_id += 1

    issue_data = {
        "uuid": issue_uuid,
        "author_id": db_user.id,
        "author_name": f"{db_user.first_name} {db_user.last_name}",
        "item_id": item_id,
        "symbol": f"PR-{last_issue_id}",
        "name": issue.name,
        "summary": issue.summary,
        "text": description,
        "text_json": issue.text_json,
        "files_issue": files,
        "tags_issue": tags,
        "color": issue.color,
        "priority": issue.priority,
        "status": "new",
        "created_at": datetime.now(timezone.utc),
    }

    new_issue = crud_issues.create_issue(db, issue_data)

    # Notification
    email_users_list = crud_settings.get_users_list_for_email_notification(db, "all")  # empty: []
    sms_users_list = []
    if email_users_list or sms_users_list:
        notify_users(sms_users_list, email_users_list, new_issue)

    event.create_new_basic_event(db, db_user, new_issue, "issue_add")
    event.open_new_basic_summary(db, "issue", new_issue.uuid, "issueTotalTime")
    event.open_new_basic_summary(db, "issue", new_issue.uuid, "issueResponseTime")

    return new_issue


@issue_router.post("/status/{issue_uuid}")
def issue_change_status(*, db: UserDB, issue_uuid: UUID, issue: IssueChangeStatus, auth_user: CurrentUser):
    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)
    if not db_issue:
        raise HTTPException(status_code=400, detail="Issue not found!")

    db_user = crud_users.get_user_by_id(db, auth_user.id)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found!")

    actions_list = crud_events.get_event_status_list(db, "issue", issue_uuid)

    actions_counter = Counter(actions_list)
    internal_value = issue.internal_value
    status = None

    match issue.status:
        # case "issue_add":
        #     if "issue_add" in actions_list:
        #         raise HTTPException(status_code=400, detail="Action Exists!")

        #     event.create_new_basic_event(db, db_user, db_issue, "issue_add")
        #     event.open_new_basic_summary(db, "issue", db_issue.uuid, "issueTotalTime")
        #     event.open_new_basic_summary(db, "issue", db_issue.uuid, "issueResponseTime")

        case "issue_accept":
            status = issue_status_accept(actions_list, db, db_issue, db_user, status)

        case "issue_reject":
            status = issue_status_reject(actions_list, db, db_issue, db_user, status)

        case "issue_add_person":
            status = issue_status_add_person(db, db_issue, db_user, internal_value, status)

        case "issue_remove_person":
            issue_status_remove_person(actions_list, db, db_issue, db_user, internal_value)

        case "issue_start_progress":
            status = issue_status_start_progress(db, db_issue, db_user, status)

        case "issue_pause":
            status = issue_status_pause(actions_counter, actions_list, db, db_issue, db_user, issue, status)

        case "issue_resume":
            status = issue_status_resume(db, db_issue, db_user, status)

        case "issue_done":
            status = issue_status_done(actions_list, db, db_issue, db_user, issue, status)

        case "issue_approve":
            if "issue_done" not in actions_list:
                raise HTTPException(status_code=400, detail="Issue not finished")

        case "issue_decline":
            if "issue_done" not in actions_list:
                raise HTTPException(status_code=400, detail="Issue not finished")

    if status in ["accepted", "rejected", "in_progress", "paused", "done"]:
        issue_update = {"status": status, "updated_at": datetime.now(timezone.utc)}
        crud_issues.update_issue(db, db_issue, issue_update)

    return {"ok": True}


def issue_status_done(actions_list, db, db_issue, db_user, issue, status):
    if "issue_done" in actions_list:
        raise HTTPException(status_code=400, detail="Task already finished!")
    event.create_new_basic_event(db, db_user, db_issue, "issue_done", description=issue.description)
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueRepairPauseTime")
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueRepairTime")
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueTotalTime")
    users_uuids = crud_events.get_basic_summary_users_uuids(db, "issue", db_issue.uuid, "issueUserActivity")
    for user_uuid in users_uuids:
        event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueUserActivity", user_uuid)
    status = "done"
    return status


def issue_status_resume(db, db_issue, db_user, status):
    event.create_new_basic_event(db, db_user, db_issue, "issue_resume")
    event.open_new_basic_summary(db, "issue", db_issue.uuid, "issueRepairTime")
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueRepairPauseTime")
    status = "in_progress"
    return status


def issue_status_pause(actions_counter, actions_list, db, db_issue, db_user, issue, status):
    if ("issue_start_progress" not in actions_list) and ((actions_counter.get("issue_start_progress") % 2) != 0):
        raise HTTPException(status_code=400, detail="No started task!")
    event.create_new_basic_event(db, db_user, db_issue, "issue_pause", description=issue.description)
    event.open_new_basic_summary(db, "issue", db_issue.uuid, "issueRepairPauseTime")
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueRepairTime")
    status = "paused"
    return status


def issue_status_start_progress(db, db_issue, db_user, status):
    event.create_new_basic_event(db, db_user, db_issue, "issue_start_progress")
    event.open_new_basic_summary(db, "issue", db_issue.uuid, "issueRepairTime")
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "acceptToStartTime")
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueRepairPauseTime")
    status = "in_progress"
    return status


def issue_status_remove_person(actions_list, db, db_issue, db_user, internal_value):
    if "issue_add_person" not in actions_list:
        raise HTTPException(status_code=400, detail="No user to remove!")
    event.create_new_basic_event(db, db_user, db_issue, "issue_remove_person", internal_value=internal_value)
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueUserActivity", internal_value)


def issue_status_add_person(db, db_issue, db_user, internal_value, status):
    event.create_new_basic_event(db, db_user, db_issue, "issue_add_person", internal_value=internal_value)
    event.open_new_basic_summary(db, "issue", db_issue.uuid, "issueUserActivity", internal_value=internal_value)
    # TODO: now only frontend is checking if users is not added twice in row, add backend validation
    status = "assigned"
    user_db_id = None
    sms_notifications = []
    email_users = []
    if internal_value:
        user_db_id = crud_users.get_user_by_uuid(db, is_valid_uuid(internal_value))
    if user_db_id:
        email_users = crud_settings.get_users_list_for_email_notification(db, "assigned_to_me", user_db_id.id)
    notify_users(sms_notifications, email_users, db_issue)
    return status


def issue_status_reject(actions_list, db, db_issue, db_user, status):
    if ("issue_reject" in actions_list) or ("issue_accept" in actions_list):
        raise HTTPException(status_code=400, detail="Action Exists!")
    event.create_new_basic_event(db, db_user, db_issue, "issue_reject")
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueResponseTime")
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueTotalTime")
    users_uuids = crud_events.get_basic_summary_users_uuids(db, "issue", db_issue.uuid, "issueUserActivity")
    for user_uuid in users_uuids:
        event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueUserActivity", user_uuid)
    status = "rejected"
    return status


def issue_status_accept(actions_list, db, db_issue, db_user, status):
    if "issue_accept" in actions_list:
        raise HTTPException(status_code=400, detail="Action Exists!")
    event.create_new_basic_event(db, db_user, db_issue, "issue_accept")
    event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueResponseTime")
    event.open_new_basic_summary(db, "issue", db_issue.uuid, "acceptToStartTime")
    # event.close_new_basic_summary(db, "issue", db_issue.uuid, "issueTotalTime")
    status = "accepted"
    return status


@issue_router.patch("/{issue_uuid}", response_model=IssueResponse)
def issue_edit(*, db: UserDB, issue_uuid: UUID, issue: IssueEditIn, auth_user: CurrentUser):
    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)
    if not db_issue:
        raise HTTPException(status_code=400, detail="Issue not found!")

    issue_data = issue.model_dump(exclude_unset=True)

    files = []
    if ("files" in issue_data) and (issue_data["files"] is not None):
        for file in db_issue.files_issue:
            db_issue.files_issue.remove(file)
        for file in issue_data["files"]:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

        issue_data["files_issue"] = files
        del issue_data["files"]

    tags = []
    if ("tags" in issue_data) and (issue_data["tags"] is not None):
        for tag in db_issue.tags_issue:
            db_issue.tags_issue.remove(tag)
        for tag in issue_data["tags"]:
            db_tag = crud_tags.get_tag_by_uuid(db, tag)
            if db_tag:
                tags.append(db_tag)

        issue_data["tags_issue"] = tags
        del issue_data["tags"]

    users = []
    if ("users" in issue_data) and (issue_data["users"] is not None):
        for user in db_issue.users_issue:
            db_issue.users_issue.remove(user)
        for user in issue_data["users"]:
            db_user = crud_users.get_user_by_uuid(db, user)
            if db_user:
                users.append(db_user)

        issue_data["users_issue"] = users
        del issue_data["users"]

    if ("text_html" in issue_data) and (issue_data["text_html"] is not None):
        issue_data["text"] = BeautifulSoup(issue.text_html, "html.parser").get_text()

    issue_data["updated_at"] = datetime.now(timezone.utc)

    new_issue = crud_issues.update_issue(db, db_issue, issue_data)

    return new_issue


@issue_router.delete("/{issue_uuid}", response_model=StandardResponse)
def issue_delete(*, db: UserDB, issue_uuid: UUID, auth_user: CurrentUser):
    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)

    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    print("DELETE files")
    for file in db_issue.files_issue:
        db_file = crud_files.get_file_by_uuid(db, file.uuid)
        print(db_file.file_name)

    db.delete(db_issue)
    db.commit()

    return {"ok": True}
