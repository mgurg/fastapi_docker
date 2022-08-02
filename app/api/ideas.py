from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Params, paginate
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import crud_ideas
from app.db import get_db
from app.models.models import Idea
from app.schemas.schemas import IdeaIndexResponse
from app.service.bearer_auth import has_token

idea_router = APIRouter()


@idea_router.get("/")  # , response_model=Page[IdeaIndexResponse]
async def ideas_get_all(
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
async def ideas_get_one(*, db: Session = Depends(get_db), idea_uuid: UUID, auth=Depends(has_token)):

    idea = crud_ideas.get_idea_by_uuid(db, idea_uuid)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    return idea
