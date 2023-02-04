import base64
import json
import re
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params, paginate
from sentry_sdk import capture_exception
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import crud_auth, crud_files, crud_ideas, crud_users
from app.db import get_db, get_public_db
from app.models.models import Idea
from app.schemas.requests import IdeaAddIn, IdeaEditIn, IdeasVotesIn
from app.schemas.responses import IdeaIndexResponse, IdeaSummaryResponse, StandardResponse

# from app.schemas.schemas import IdeaIndexResponse
from app.service.aws_s3 import generate_presigned_url
from app.service.bearer_auth import has_token
from app.service.mentions import Mention

idea_router = APIRouter()


@idea_router.get("/stats", response_model=IdeaSummaryResponse)
def ideas_get_summary(*, db: Session = Depends(get_db), auth=Depends(has_token)):

    ideas_summary = crud_ideas.get_ideas_summary(db)
    if not ideas_summary:
        return {"accepted": 0, "pending": 0, "rejected": 0, "todo": 0}

    ideas_status = dict(ideas_summary)

    for status in ["pending", "accepted", "rejected", "todo"]:
        ideas_status.setdefault(status, 0)

    return ideas_status


@idea_router.get("/", response_model=Page[IdeaIndexResponse])  # , response_model=Page[IdeaIndexResponse]
def ideas_get_all(
    *,
    db: Session = Depends(get_db),
    sortOrder: str = "asc",
    sortColumn: str = "name",
    search: str = None,
    status: str = None,
    hasImg: bool = None,
    params: Params = Depends(),
    auth=Depends(has_token),
):

    all_filters = []

    if status is not None:
        all_filters.append(Idea.status == status)
    if hasImg is True:
        all_filters.append(Idea.files_idea.any())
        # all_filters.append(Idea.files_idea.any(Files.size > 279824))
    if search is not None:
        all_filters.append(func.concat(Idea.name, " ", Idea.description).ilike(f"%{search}%"))

    sortTable = {"name": "name", "age": "created_at", "counter": "upvotes"}

    ideas = crud_ideas.get_ideas(db, all_filters, sortTable[sortColumn], sortOrder)

    return paginate(ideas, params)


@idea_router.get("/{idea_uuid}", response_model=IdeaIndexResponse, name="ideas:Item")
def ideas_get_one(*, db: Session = Depends(get_db), idea_uuid: UUID, request: Request, auth=Depends(has_token)):
    idea = crud_ideas.get_idea_by_uuid(db, idea_uuid)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    try:
        for picture in idea.files_idea:
            picture.url = generate_presigned_url(
                request.headers.get("tenant", "public"), "_".join([str(picture.uuid), picture.file_name])
            )
    except Exception as e:
        capture_exception(e)

    return idea


@idea_router.get("/user/{user_uuid}", response_model=Page[IdeaIndexResponse])
def ideas_get_by_user(
    *, db: Session = Depends(get_db), user_uuid: UUID, params: Params = Depends(), auth=Depends(has_token)
):

    db_user = crud_users.get_user_by_uuid(db, user_uuid)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_ideas = crud_ideas.get_idea_by_user_id(db, db_user.id)

    return paginate(db_ideas, params)


@idea_router.post("/", response_model=StandardResponse)
def idea_add(*, db: Session = Depends(get_db), idea: IdeaAddIn, auth=Depends(has_token)):

    files = []
    if idea.files is not None:
        for file in idea.files:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

    html = idea.text_html
    soup = BeautifulSoup(html, "html.parser")
    # title = soup.find("h1").get_text().strip()
    # for s in soup.select("h1"):
    #     s.extract()
    description = soup.get_text()

    json_object = json.dumps(idea.text_json)

    Mention(json_object, "groupMention").process()
    Mention(json_object, "userMention").process()

    idea_data = {
        "uuid": str(uuid4()),
        "author_id": auth["user_id"],
        "color": idea.color,
        "name": idea.name,
        "summary": description,
        "text": description,
        "text_json": idea.text_json,
        "upvotes": 0,
        "downvotes": 0,
        "status": "pending",
        "files_idea": files,
        "created_at": datetime.now(timezone.utc),
    }

    crud_ideas.create_idea(db, idea_data)

    return {"ok": True}


@idea_router.post("/new_idea/{idea_id}", name="idea:Add")
def idea_add_anonymous_one(*, public_db: Session = Depends(get_public_db), idea_id: str):

    pattern = re.compile(r"^[a-z2-9]{2,3}\+[a-z2-9]{2,3}$")
    if pattern.match(idea_id):

        company, board = idea_id.split("+")

        db_company = crud_auth.get_public_company_by_qr_id(public_db, company)

        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")

        # https://strftime.org
        token_valid_to = (datetime.now(timezone.utc) + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        fake_token = f"{db_company.tenant_id}.{token_valid_to}"

        message_bytes = fake_token.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode("ascii")

        # db_setting_mode = session.execute(
        #     select(Setting)
        #     .where(Setting.account_id == db_account.account_id)
        #     .where(Setting.entity == "idea_registration_mode")
        # ).scalar_one_or_none()

        # db_setting_mail = session.execute(
        #     select(Setting)
        #     .where(Setting.account_id == db_account.account_id)
        #     .where(Setting.entity == "issue_registration_email")
        # ).scalar_one_or_none()

        mode = "anonymous"
        email = "email@email.com"

        return {"token": base64_message, "mode": mode, "email": email}
    else:
        raise HTTPException(status_code=404, detail="Incorrect id")


@idea_router.post("/vote", response_model=StandardResponse, name="idea:Add")
def idea_add_vote_one(*, db: Session = Depends(get_db), vote: IdeasVotesIn, auth=Depends(has_token)):

    db_idea = crud_ideas.get_idea_by_uuid(db, vote.idea_uuid)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    vote_data = vote.dict(exclude_unset=True)
    if vote_data["vote"] == "up":
        idea_data = {"upvotes": int(db_idea.upvotes) + 1}
    elif vote_data["vote"] == "down":
        idea_data = {"downvotes": int(db_idea.downvotes) + 1}
    else:
        raise HTTPException(status_code=404, detail="Invalid vote type")

    crud_ideas.update_idea(db, db_idea, idea_data)

    return {"ok": True}


@idea_router.patch("/{idea_uuid}", response_model=StandardResponse)
def idea_edit(*, db: Session = Depends(get_db), idea_uuid: UUID, idea: IdeaEditIn, auth=Depends(has_token)):

    db_idea = crud_ideas.get_idea_by_uuid(db, idea_uuid)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    json_object = json.dumps(idea.text_json)

    idea_data = idea.dict(exclude_unset=True)
    if "vote" in idea_data:
        del idea_data["vote"]

    files = []
    if ("files" in idea_data) and (idea_data["files"] is not None):
        for file in db_idea.files_idea:
            db_idea.files_idea.remove(file)
        for file in idea_data["files"]:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

        idea_data["files_idea"] = files
        del idea_data["files"]

        idea_data["body_json"] = json_object

    crud_ideas.update_idea(db, db_idea, idea_data)

    return {"ok": True}


@idea_router.delete("/{idea_uuid}", response_model=StandardResponse, name="idea:Delete")
def idea_delete_one(*, db: Session = Depends(get_db), idea_uuid: UUID, auth=Depends(has_token)):

    db_idea = crud_ideas.get_idea_by_uuid(db, idea_uuid)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Delete Files
    for files_idea in db_idea.files_idea:
        db_file = crud_files.get_file_by_id(db, files_idea.id)
        db_idea.files_idea.remove(files_idea)
        db.delete(db_file)
        db.commit()

    db.delete(db_idea)
    db.commit()

    # update_package = {"deleted_at": datetime.now(timezone.utc)}  # soft delete
    # for key, value in update_package.items():
    #     setattr(db_idea, key, value)

    # session.add(db_idea)
    # session.commit()
    # session.refresh(db_idea)

    return {"ok": True}
