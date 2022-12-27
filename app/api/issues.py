from datetime import datetime, timezone
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params, paginate
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session

from app.crud import crud_auth, crud_files, crud_issues, crud_items, crud_users
from app.db import engine, get_db
from app.schemas.requests import IssueAddIn, IssueEditIn
from app.schemas.responses import IssueIndexResponse, IssueResponse, StandardResponse
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


@issue_router.post("/", response_model=IssueIndexResponse)
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

    description = BeautifulSoup(issue.text_html, "html.parser").get_text()

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

    return new_issue


@issue_router.patch("/{issue_uuid}", response_model=IssueIndexResponse)
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
