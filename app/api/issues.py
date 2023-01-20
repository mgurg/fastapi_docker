from datetime import datetime, timezone
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params, paginate
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session

from app.crud import (
    crud_auth,
    crud_events,
    crud_files,
    crud_issues,
    crud_items,
    crud_settings,
    crud_users,
)
from app.db import engine, get_db
from app.schemas.requests import IssueAddIn, IssueChangeStatus, IssueEditIn
from app.schemas.responses import (
    EventTimelineResponse,
    IssueIndexResponse,
    IssueResponse,
    IssueSummaryResponse,
    StandardResponse,
)
from app.service import event
from app.service.aws_s3 import generate_presigned_url
from app.service.bearer_auth import has_token
from app.service.notifications import notify_users

issue_router = APIRouter()


@issue_router.get("/", response_model=Page[IssueIndexResponse])
def issue_get_all(
    *,
    db: Session = Depends(get_db),
    params: Params = Depends(),
    search: str | None = None,
    status: str = "active",
    user_uuid: UUID | None = None,
    priority: str | None = None,
    dateFrom: datetime | None = None,
    dateTo: datetime | None = None,
    field: str = "created_at",
    order: str = "asc",
    auth=Depends(has_token),
):
    if field not in ["created_at", "name", "priority", "status"]:
        field = "created_at"

    user_id = None
    if user_uuid is not None:
        db_user = crud_users.get_user_by_uuid(db, user_uuid)
        if db_user is None:
            raise HTTPException(status_code=401, detail="User not found")
        user_id = db_user.id

    db_issues = crud_issues.get_issues(db, search, status, user_id, priority, field, order, dateFrom, dateTo)
    return paginate(db_issues, params)


@issue_router.get("/stats", response_model=IssueSummaryResponse)
def issue_get_summary(*, db: Session = Depends(get_db), auth=Depends(has_token)):

    ideas_summary = crud_issues.get_issue_summary(db)
    if not ideas_summary:
        return {
            "new": 0,
            "accepted": 0,
            "rejected": 0,
            "assigned": 0,
            "in_progress": 0,
            "paused": 0,
            "resolved": 0,
        }

    ideas_status = dict(ideas_summary)

    for status in ["new", "accepted", "rejected", "assigned", "in_progress", "paused", "resolved"]:
        ideas_status.setdefault(status, 0)

    return ideas_status


@issue_router.get("/timeline/{issue_uuid}", response_model=list[EventTimelineResponse])
def item_get_timeline_history(
    *, db: Session = Depends(get_db), issue_uuid: UUID, thread_resource: str | None = None, auth=Depends(has_token)
):
    # db_item = crud_items.get_item_by_uuid(db, issue_uuid)
    # if not db_item:
    #     raise HTTPException(status_code=400, detail="Item not found!")

    db_events = crud_events.get_events_by_thread(db, issue_uuid, thread_resource)
    return db_events


@issue_router.get("/{issue_uuid}", response_model=IssueResponse)  # , response_model=Page[UserIndexResponse]
def issue_get_one(*, db: Session = Depends(get_db), issue_uuid: UUID, request: Request, auth=Depends(has_token)):
    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)

    if not db_issue:
        raise HTTPException(status_code=400, detail="Issue not found!")

    try:
        for picture in db_issue.files_issue:
            picture.url = generate_presigned_url(
                request.headers.get("tenant", "public"),
                "_".join([str(picture.uuid), picture.file_name]),
            )
    except Exception as e:
        capture_exception(e)

    return db_issue


@issue_router.post("/", response_model=IssueResponse)  #
def issue_add(*, db: Session = Depends(get_db), request: Request, issue: IssueAddIn, auth=Depends(has_token)):

    tenant_id = request.headers.get("tenant", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Unknown Company!")

    company = None
    schema_translate_map = dict(tenant="public")
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable) as public_db:
        company = crud_auth.get_public_company_by_tenant_id(public_db, tenant_id)
    if not company:
        raise HTTPException(status_code=400, detail="Unknown Company!")

    files = []
    if issue.files is not None:
        for file in issue.files:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

    issue_uuid = str(uuid4())

    db_user = crud_users.get_user_by_id(db, auth["user_id"])
    author_name = "anonymous"
    if db_user:
        author_name = f"{db_user.first_name} {db_user.last_name}"

    db_item = crud_items.get_item_by_uuid(db, issue.item_uuid)
    item_id = None
    if db_item:
        item_id = db_item.id

    description = None
    if issue.text_html is not None:
        description = BeautifulSoup(issue.text_html, "html.parser").get_text()  # TODO add fix when empty

    issue_data = {
        "uuid": issue_uuid,
        "author_id": auth["user_id"],
        "author_name": author_name,
        "item_id": item_id,
        "name": issue.name,
        "summary": issue.summary,
        "text": description,
        "text_json": issue.text_json,
        "files_issue": files,
        "color": issue.color,
        "priority": issue.priority,
        "status": "new",
        "created_at": datetime.now(timezone.utc),
    }

    new_issue = crud_issues.create_issue(db, issue_data)

    # Notification
    email_notifications = crud_settings.get_users_for_email_notification(db, "all")
    sms_notifications = crud_settings.get_users_for_sms_notification(db, "all")

    keys = ("phone", "mode")
    list_of_sms_notifications = [dict(zip(keys, values)) for values in sms_notifications]

    keys = ("email", "mode")
    list_of_email_notifications = [dict(zip(keys, values)) for values in email_notifications]
    notify_users(list_of_sms_notifications, list_of_email_notifications, new_issue)

    event.create_new_item_event(
        db, db_user, db_item, new_issue, "issue_add", "Issue added", new_issue.name, new_issue.text
    )
    if db_item is not None:
        event.create_new_item_event_statistic(db, db_item, new_issue, "issueStartTime")
        event.create_new_item_event_statistic(db, db_item, new_issue, "issueTotalTime")

    return new_issue


@issue_router.post("/status/{issue_uuid}")
def issue_change_status(
    *, db: Session = Depends(get_db), issue_uuid: UUID, issue: IssueChangeStatus, auth=Depends(has_token)
):

    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)
    if not db_issue:
        raise HTTPException(status_code=400, detail="Issue not found!")

    db_item = crud_items.get_item_by_id(db, db_issue.item_id)
    # if not db_item:
    #     raise HTTPException(status_code=400, detail="Item not found!")

    db_issue.status

    db_user = crud_users.get_user_by_id(db, auth["user_id"])
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found!")
    if db_user:
        f"{db_user.first_name} {db_user.last_name}"

    status = None
    match issue.status:
        case "issue_accept":
            event.create_new_item_event(
                db, db_user, db_item, db_issue, "issue_accept", issue.name, issue.description, issue.value
            )
            event.close_event_statistics(db, db_issue, "issueStartTime")
            status = "accepted"

        case "issue_reject":
            event.create_new_item_event(
                db, db_user, db_item, db_issue, "issue_reject", issue.name, issue.description, issue.value
            )
            event.close_event_statistics(db, db_issue, "issueStartTime")
            event.close_event_statistics(db, db_issue, "issueTotalTime")
            status = "rejected"

        case "issue_change_assigned_person":
            event.create_new_item_event(
                db,
                db_user,
                db_item,
                db_issue,
                "issue_change_assigned_person",
                issue.name,
                issue.description,
                issue.value,
            )
            status = "assigned"

        case "issue_start_progress":
            event.create_new_item_event(db, db_user, db_item, db_issue, "issue_start_progress", issue.name)
            event.create_new_item_event_statistic(db, db_item, db_issue, "issueRepairTime")
            status = "in_progress"

        case "issue_pause":
            event.create_new_item_event(
                db, db_user, db_item, db_issue, "issue_pause", issue.name, issue.description, issue.value
            )
            event.close_event_statistics(db, db_issue, "issueRepairTime")
            event.create_new_item_event_statistic(db, db_item, db_issue, "issueRepairPauseTime")
            status = "paused"

        case "issue_resume":
            event.create_new_item_event(db, db_user, db_item, db_issue, "issue_resume", issue.name)
            event.close_event_statistics(db, db_issue, "issueRepairPauseTime")
            event.create_new_item_event_statistic(db, db_item, db_issue, "issueRepairTime")
            status = "in_progress"

        case "issue_resolve":
            event.create_new_item_event(
                db, db_user, db_item, db_issue, "issue_resolve", issue.name, issue.description, issue.value
            )
            event.close_event_statistics(db, db_issue, "issueRepairPauseTime")
            event.close_event_statistics(db, db_issue, "issueRepairTime")
            event.close_event_statistics(db, db_issue, "issueTotalTime")
            status = "resolved"

    if status in ["accepted", "rejected", "in_progress", "paused", "resolved"]:
        issue_update = {"status": status, "updated_at": datetime.now(timezone.utc)}
        crud_issues.update_issue(db, db_issue, issue_update)

    return {"ok": True}


@issue_router.patch("/{issue_uuid}", response_model=IssueResponse)
def issue_edit(*, db: Session = Depends(get_db), issue_uuid: UUID, issue: IssueEditIn, auth=Depends(has_token)):

    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)
    if not db_issue:
        raise HTTPException(status_code=400, detail="Issue not found!")

    issue_data = issue.dict(exclude_unset=True)

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
def issue_delete(*, db: Session = Depends(get_db), issue_uuid: UUID, auth=Depends(has_token)):

    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)

    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(db_issue)
    db.commit()

    return {"ok": True}
