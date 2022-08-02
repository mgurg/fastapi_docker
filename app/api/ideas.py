from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import crud_files, crud_ideas
from app.db import get_db
from app.models.models import Idea
from app.schemas.requests import IdeaAddIn
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
