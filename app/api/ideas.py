import base64
import re
from datetime import datetime, time, timedelta
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, Params, paginate

# from sqlmodel import Session, select
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db import get_session
from app.model.model import Account, File, Idea, IdeaVote, Setting, User
from app.schema.schema import (
    IdeaAddIn,
    IdeaEditIn,
    IdeaIndexResponse,
    IdeasVotesIn,
    StandardResponse,
)
from app.service.bearer_auth import has_token

idea_router = APIRouter()


@idea_router.get("/", response_model=Page[IdeaIndexResponse], name="ideas:List")
async def ideas_get_all(
    *,
    session: Session = Depends(get_session),
    # offset: int = 0,
    # limit: int = Query(default=100, lte=100),
    sortOrder: str = "asc",
    sortColumn: str = "title",
    search: str = None,
    status: str = None,
    hasImg: bool = None,
    params: Params = Depends(),
    auth=Depends(has_token),
):

    all_filters = []

    sortTable = {"title": "title", "age": "created_at", "counter": "upvotes"}

    if status is not None:
        all_filters.append(Idea.status == status)

    if hasImg is True:
        all_filters.append(Idea.pictures.any())
        # all_filters.append(Idea.pictures.any(Files.size > 279824))

    if search is not None:
        all_filters.append(func.concat(Idea.title, " ", Idea.description).ilike(f"%{search}%"))
    # print(all_filters)

    ideas = (
        session.execute(
            select(Idea)
            .where(Idea.account_id == auth["account"])
            .where(Idea.deleted_at.is_(None))
            .filter(*all_filters)
            .order_by(text(f"{sortTable[sortColumn]} {sortOrder}"))
            # .offset(offset)
            # .limit(limit)
        )
        .scalars()
        .all()
    )

    return paginate(ideas, params)


@idea_router.get("/{idea_uuid}", response_model=IdeaIndexResponse, name="ideas:Item")
async def ideas_get_one(*, session: Session = Depends(get_session), idea_uuid: UUID, auth=Depends(has_token)):

    idea = session.execute(
        select(Idea)
        .where(Idea.account_id == auth["account"])
        .where(Idea.uuid == idea_uuid)
        .where(Idea.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    return idea


@idea_router.get("/user/{user_uuid}", response_model=Page[IdeaIndexResponse], name="ideas:UserItems")
async def ideas_get_one(
    *, session: Session = Depends(get_session), user_uuid: UUID, params: Params = Depends(), auth=Depends(has_token)
):

    db_user = session.execute(
        select(User)
        .where(User.account_id == auth["account"])
        .where(User.uuid == user_uuid)
        .where(User.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    ideas = (
        session.execute(
            select(Idea)
            .where(Idea.account_id == auth["account"])
            .where(Idea.author_id == db_user.id)
            .where(Idea.deleted_at.is_(None))
        )
        .scalars()
        .all()
    )

    return paginate(ideas, params)


@idea_router.get("/vote_last/{idea_uuid}", name="ideas:Item")
async def ideas_get_last_vote(*, session: Session = Depends(get_session), idea_uuid: UUID, auth=Depends(has_token)):

    db_idea = session.execute(
        select(Idea)
        .where(Idea.account_id == auth["account"])
        .where(Idea.uuid == idea_uuid)
        .where(Idea.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    db_last_vote = (
        session.execute(
            select(IdeaVote)
            .where(IdeaVote.idea_id == db_idea.id)
            .where(IdeaVote.account_id == auth["account"])
            .where(IdeaVote.user_id == auth["user"])
            .order_by(IdeaVote.id.desc())
        )
        .scalars()
        .first()
    )

    if not db_last_vote:
        return {"vote": None}

    return {"vote": db_last_vote.vote}


@idea_router.post("/new_idea/{idea_id}", name="idea:Add")
async def idea_add_anonymous_one(*, session: Session = Depends(get_session), idea_id: str):

    pattern = re.compile("^[a-z2-9]{2,3}\+[a-z2-9]{2,3}$")
    if pattern.match(idea_id):

        company, board = idea_id.split("+")

        db_account = session.execute(select(Account).where(Account.company_id == company)).scalar_one_or_none()

        if not db_account:
            raise HTTPException(status_code=404, detail="Account not found")

        message = company + "." + (datetime.utcnow() + timedelta(minutes=15)).strftime("%Y-%m-%d %H-%M-%S")
        message_bytes = message.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode("ascii")

        db_setting_mode = session.execute(
            select(Setting)
            .where(Setting.account_id == db_account.account_id)
            .where(Setting.entity == "idea_registration_mode")
        ).scalar_one_or_none()

        db_setting_mail = session.execute(
            select(Setting)
            .where(Setting.account_id == db_account.account_id)
            .where(Setting.entity == "issue_registration_email")
        ).scalar_one_or_none()

        return {"token": base64_message, "mode": db_setting_mode.value, "email": db_setting_mail.value}
    else:
        raise HTTPException(status_code=404, detail="Incorrect id")
    # %!#+23456789:=?@ABCDEFGHJKLMNPRS
    # TUVWXYZabcdefghijkmnopqrstuvwxyz

    # abcdefghijkmnopqrstuvwxyz23456789
    # ABCDEFGHJKLMNPRSTUVWXYZ23456789


@idea_router.post("/", response_model=StandardResponse, name="idea:Add")
async def user_add_one(*, session: Session = Depends(get_session), idea: IdeaAddIn, auth=Depends(has_token)):

    res = IdeaAddIn.from_orm(idea)

    files = []
    if res.files is not None:
        for file in res.files:
            db_file = session.execute(
                select(File).where(File.uuid == file).where(File.deleted_at.is_(None))
            ).scalar_one_or_none()
            if db_file:
                files.append(db_file)

    new_idea = Idea(
        uuid=str(uuid4()),
        account_id=auth["account"],
        author_id=auth["user"],
        upvotes=0,
        downvotes=0,
        status="pending",
        color=res.color,
        title=res.title,
        description=res.description,
        pictures=files,
        created_at=datetime.utcnow(),
    )

    session.add(new_idea)
    session.commit()
    session.refresh(new_idea)

    return {"ok": True}


@idea_router.post("/vote", response_model=StandardResponse, name="idea:Add")
async def idea_add_vote_one(*, session: Session = Depends(get_session), vote: IdeasVotesIn, auth=Depends(has_token)):
    res = IdeasVotesIn.from_orm(vote)

    db_idea = session.execute(
        select(Idea)
        .where(Idea.account_id == auth["account"])
        .where(Idea.uuid == res.idea_uuid)
        .where(Idea.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    db_last_vote = (
        session.execute(
            select(IdeaVote)
            .where(IdeaVote.idea_id == db_idea.id)
            .where(IdeaVote.account_id == auth["account"])
            .where(IdeaVote.user_id == auth["user"])
            .order_by(IdeaVote.id.desc())
        )
        .scalars()
        .first()
    )

    if (db_last_vote is not None) and (db_last_vote.vote == res.vote):
        raise HTTPException(status_code=404, detail="Duplicated vote")

    if res.vote == "up":
        db_idea.upvotes += 1
    elif res.vote == "down":
        db_idea.downvotes += 1
    else:
        raise HTTPException(status_code=404, detail="Invalid vote type")

    new_vote = IdeaVote(
        uuid=str(uuid4()),
        account_id=auth["account"],
        idea_id=db_idea.id,
        user_id=auth["user"],
        vote=res.vote,
        created_at=datetime.utcnow(),
    )

    session.add(new_vote)
    session.commit()
    session.refresh(new_vote)

    session.add(db_idea)
    session.commit()
    session.refresh(db_idea)
    return {"ok": True}


@idea_router.patch("/{idea_uuid}", response_model=StandardResponse, name="task:Tasks")
async def user_get_all(
    *, session: Session = Depends(get_session), idea_uuid: UUID, task: IdeaEditIn, auth=Depends(has_token)
):

    db_idea = session.execute(select(Idea).where(Idea.uuid == idea_uuid)).scalar_one_or_none()
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    idea_data = task.dict(exclude_unset=True)
    if "vote" in idea_data:
        del idea_data["vote"]

    # files = []
    # if ("files" in idea_data) and (idea_data["files"] is not None):
    #     for file in db_idea.file:
    #         db_idea.file.remove(file)
    #     for file in idea_data["files"]:
    #         db_file = session.execute(
    #             select(File).where(File.uuid == file).where(File.deleted_at.is_(None))
    #         ).scalar_one_or_none()
    #         if db_file:
    #             files.append(db_file)

    #     idea_data["file"] = files
    #     del idea_data["files"]

    for key, value in idea_data.items():
        setattr(db_idea, key, value)

    session.add(db_idea)
    session.commit()
    session.refresh(db_idea)

    return {"ok": True}


@idea_router.delete("/{idea_uuid}", response_model=StandardResponse, name="idea:Delete")
async def idea_delete_one(*, session: Session = Depends(get_session), idea_uuid: UUID, auth=Depends(has_token)):

    db_idea = session.execute(
        select(Idea).where(Idea.account_id == auth["account"]).where(Idea.uuid == idea_uuid)
    ).scalar_one_or_none()

    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # db_idea.events.remove()

    # Delete Files
    for pictures in db_idea.pictures:
        db_file = session.execute(select(File).where(File.id == pictures.id)).one()
        db_idea.pictures.remove(pictures)
        session.delete(db_file)
        session.commit()

    session.delete(db_idea)
    session.commit()

    # update_package = {"deleted_at": datetime.utcnow()}  # soft delete
    # for key, value in update_package.items():
    #     setattr(db_idea, key, value)

    # session.add(db_idea)
    # session.commit()
    # session.refresh(db_idea)

    return {"ok": True}
