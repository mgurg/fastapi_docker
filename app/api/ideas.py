import base64
import re
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import crud_auth, crud_files, crud_ideas, crud_users
from app.db import get_db, get_public_db
from app.models.models import Idea
from app.schemas.requests import IdeaAddIn, IdeasVotesIn
from app.schemas.responses import StandardResponse
from app.schemas.schemas import IdeaIndexResponse
from app.service.bearer_auth import has_token

idea_router = APIRouter()


@idea_router.get("/", response_model=Page[IdeaIndexResponse])  # , response_model=Page[IdeaIndexResponse]
def ideas_get_all(
    *,
    db: Session = Depends(get_db),
    sortOrder: str = "asc",
    sortColumn: str = "title",
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
        all_filters.append(Idea.pictures.any())
        # all_filters.append(Idea.pictures.any(Files.size > 279824))
    if search is not None:
        all_filters.append(func.concat(Idea.title, " ", Idea.description).ilike(f"%{search}%"))

    sortTable = {"title": "title", "age": "created_at", "counter": "upvotes"}

    ideas = crud_ideas.get_ideas(db, all_filters, sortTable[sortColumn], sortOrder)

    return paginate(ideas, params)


@idea_router.get("/{idea_uuid}", response_model=IdeaIndexResponse, name="ideas:Item")
def ideas_get_one(*, db: Session = Depends(get_db), idea_uuid: UUID, auth=Depends(has_token)):

    idea = crud_ideas.get_idea_by_uuid(db, idea_uuid)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    return idea


@idea_router.get("/user/{user_uuid}", response_model=Page[IdeaIndexResponse])
async def ideas_get_by_user(
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

    idea_data = {
        "uuid": str(uuid4()),
        "author_id": auth["user_id"],
        "color": idea.color,
        "title": idea.title,
        "description": idea.description,
        "upvotes": 0,
        "downvotes": 0,
        "status": "pending",
        "pictures": files,
        "created_at": datetime.utcnow(),
    }

    crud_ideas.create_idea(db, idea_data)

    return {"ok": True}


@idea_router.post("/new_idea/{idea_id}", name="idea:Add")
async def idea_add_anonymous_one(*, shared_db: Session = Depends(get_public_db), idea_id: str):

    pattern = re.compile("^[a-z2-9]{2,3}\+[a-z2-9]{2,3}$")
    if pattern.match(idea_id):

        company, board = idea_id.split("+")

        db_company = crud_auth.get_public_company_by_qr_id(shared_db, company)

        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")

        message = (
            db_company.tenant_id + "." + (datetime.utcnow() + timedelta(minutes=15)).strftime("%Y-%m-%d %H-%M-%S")
        )
        message_bytes = message.encode("ascii")
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
async def idea_add_vote_one(*, db: Session = Depends(get_db), vote: IdeasVotesIn, auth=Depends(has_token)):
    res = IdeasVotesIn.from_orm(vote)

    db_idea = crud_ideas.get_idea_by_uuid(db, vote.idea_uuid)

    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    if vote.vote == "up":
        idea_data = {"upvotes": db_idea.upvotes + 1}
    elif vote.vote == "down":
        idea_data = {"downvotes": db_idea.downvotes + 1}
    else:
        raise HTTPException(status_code=404, detail="Invalid vote type")

    crud_ideas.update_idea(db, db_idea, idea_data)

    return {"ok": True}


@idea_router.delete("/{idea_uuid}", response_model=StandardResponse, name="idea:Delete")
async def idea_delete_one(*, db: Session = Depends(get_db), idea_uuid: UUID, auth=Depends(has_token)):

    db_idea = crud_ideas.get_idea_by_uuid(db, idea_uuid)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Delete Files
    for pictures in db_idea.pictures:
        db_file = crud_files.get_file_by_id(db, pictures.id)
        db_idea.pictures.remove(pictures)
        db.delete(db_file)
        db.commit()

    db.delete(db_idea)
    db.commit()

    # update_package = {"deleted_at": datetime.utcnow()}  # soft delete
    # for key, value in update_package.items():
    #     setattr(db_idea, key, value)

    # session.add(db_idea)
    # session.commit()
    # session.refresh(db_idea)

    return {"ok": True}
