from datetime import datetime, time, timedelta
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session
from app.model.model import Account, File, Idea
from app.schema.schema import StandardResponse
from app.service.bearer_auth import has_token

stats_router = APIRouter()


@stats_router.get("/status", name="stats:Idea.status")
async def ideas_get_all(*, session: Session = Depends(get_session), auth=Depends(has_token)):

    ideas_status = (
        session.exec(
            select(Idea.status, func.count(Idea.status))
            .where(Idea.account_id == auth["account"])
            .group_by(Idea.status)
        )
        .scalars()
        .all()
    )

    ideas_status = dict(ideas_status)

    for status in ["pending", "accepted", "rejected", "todo"]:
        ideas_status.setdefault(status, 0)

    return ideas_status
