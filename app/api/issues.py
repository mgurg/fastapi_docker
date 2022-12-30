from datetime import datetime, timezone
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params, paginate
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session

from app.crud import crud_auth, crud_files, crud_issues, crud_items, crud_users
from app.db import engine, get_db
from app.schemas.requests import IssueAddIn, IssueChangeStatus, IssueEditIn
from app.schemas.responses import IssueIndexResponse, IssueResponse, StandardResponse
from app.service import event
from app.service.aws_s3 import generate_presigned_url
from app.service.bearer_auth import has_token

issue_router = APIRouter()


@issue_router.get("/", response_model=Page[IssueIndexResponse])
def issue_get_all(
    *,
    db: Session = Depends(get_db),
    params: Params = Depends(),
    search: str = None,
    sortOrder: str = "asc",
    sortColumn: str = "name",
    auth=Depends(has_token),
):

    sortTable = {"name": "name"}

    db_issues = crud_issues.get_issues(db, search, sortTable[sortColumn], sortOrder)
    return paginate(db_issues, params)


@issue_router.get("/user/{user_uuid}", response_model=Page[IssueIndexResponse])
def issue_get_all(
    *,
    db: Session = Depends(get_db),
    user_uuid: UUID,
    params: Params = Depends(),
    search: str = None,
    sortOrder: str = "asc",
    sortColumn: str = "name",
    auth=Depends(has_token),
):

    sortTable = {"name": "name"}

    db_user = crud_users.get_user_by_uuid(db, user_uuid)

    if db_user is None:
        raise HTTPException(status_code=401, detail="User not found")

    db_issues = crud_issues.get_issues_by_user_id(db, db_user.id)
    # print("#####################")
    # print(db_issues.users_issue)
    # print(dict(db_issues))
    return paginate(db_issues, params)


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


@issue_router.post("/", response_model=IssueResponse)
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
        "status": issue.status,
        "created_at": datetime.now(timezone.utc),
    }

    new_issue = crud_issues.create_issue(db, issue_data)

    event.create_new_event(db, db_user, db_item, new_issue, "issueAdd")
    event.create_new_event_statistic(db, db_item, new_issue, "issueStartTime")
    event.create_new_event_statistic(db, db_item, new_issue, "issueTotalTime")

    return new_issue


@issue_router.post("/status/{issue_uuid}")
def issue_change_status(
    *, db: Session = Depends(get_db), issue_uuid: UUID, issue: IssueChangeStatus, auth=Depends(has_token)
):

    db_issue = crud_issues.get_issue_by_uuid(db, issue_uuid)
    if not db_issue:
        raise HTTPException(status_code=400, detail="Issue not found!")

    db_item = crud_items.get_item_by_id(db, db_issue.item_id)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found!")

    db_issue.status

    db_user = crud_users.get_user_by_id(db, auth["user_id"])
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found!")
    if db_user:
        f"{db_user.first_name} {db_user.last_name}"

    match issue.status:
        case "accept_issue":
            event.create_new_event(db, db_user, db_item, db_issue, "issueAccepted")
            event.close_event_statistics(db, db_issue, "issueStartTime")

        case "reject_issue":
            event.create_new_event(db, db_user, db_item, db_issue, "issueRejected")
            event.close_event_statistics(db, db_issue, "issueStartTime")
            event.close_event_statistics(db, db_issue, "issueTotalTime")

        case "assign_person":
            event.create_new_event(db, db_user, db_item, db_issue, "issueAssignedPerson")

        case "in_progress_issue":
            event.create_new_event(db, db_user, db_item, db_issue, "issueRepairStart")
            event.create_new_event_statistic(db, db_item, db_issue, "issueRepairTime")

        case "pause_issue":
            event.create_new_event(db, db_user, db_item, db_issue, "issueRepairPause")
            event.close_event_statistics(db, db_issue, "issueRepairTime")
            event.create_new_event_statistic(db, db_item, db_issue, "issueRepairPauseTime")

        case "resume_issue":
            event.create_new_event(db, db_user, db_item, db_issue, "issueRepairResume")
            event.close_event_statistics(db, db_issue, "issueRepairPauseTime")
            event.create_new_event_statistic(db, db_item, db_issue, "issueRepairTime")

        case "resolved_issue":
            event.create_new_event(db, db_user, db_item, db_issue, "issueRepairFinish")
            event.close_event_statistics(db, db_issue, "issueRepairPauseTime")
            event.close_event_statistics(db, db_issue, "issueRepairTime")
            event.close_event_statistics(db, db_issue, "issueTotalTime")

    issue_update = {"status": issue.status, "updated_at": datetime.now(timezone.utc)}
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