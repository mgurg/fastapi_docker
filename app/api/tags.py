from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import crud_tags
from app.db import get_db
from app.schemas.requests import TagCreateIn
from app.schemas.responses import StandardResponse, TagResponse
from app.service.bearer_auth import has_token

tag_router = APIRouter()


@tag_router.get("/", response_model=list[TagResponse])
def tags_get_all(*, db: Session = Depends(get_db), auth=Depends(has_token)):
    tags = crud_tags.get_tags(db)
    return tags


@tag_router.post("/", response_model=TagResponse)
def tags_add_one(*, db: Session = Depends(get_db), tag: TagCreateIn, auth=Depends(has_token)):

    tag_data = {
        "uuid": str(uuid4()),
        "name": tag.name,
        "color": tag.color,
        "icon": tag.icon,
        "author_id": auth["user_id"],
        "created_at": datetime.now(timezone.utc),
    }

    tag = crud_tags.create_tag(db, tag_data)

    return tag


@tag_router.patch("/{tag_uuid}", response_model=TagResponse)
def tags_edit_one(*, db: Session = Depends(get_db), tag_uuid: UUID, auth=Depends(has_token)):
    db_tag = crud_tags.get_tag_by_uuid(db, tag_uuid)
    return db_tag


@tag_router.delete("/{tag_uuid}", response_model=StandardResponse)
def tags_delete_one(*, db: Session = Depends(get_db), tag_uuid: UUID, auth=Depends(has_token)):
    db_user = crud_tags.get_tag_by_uuid(db, tag_uuid)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.email

    db.delete(db_user)
    db.commit()

    return {"ok": True}
