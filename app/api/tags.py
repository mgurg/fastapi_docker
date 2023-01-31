from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.crud import crud_tags
from app.db import get_db
from app.schemas.responses import TagResponse
from app.service.bearer_auth import has_token

tag_router = APIRouter()


@tag_router.get("/", response_model=list[TagResponse])
def tags_get_all(*, db: Session = Depends(get_db), auth=Depends(has_token)):
    tags = crud_tags.get_tags(db)
    return tags
