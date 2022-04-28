import base64
import re
from datetime import datetime, time, timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import (
    Accounts,
    Files,
    IdeaAddIn,
    IdeaEditIn,
    IdeaIndexResponse,
    Ideas,
    IdeasVotes,
    IdeasVotesIn,
    StandardResponse,
)
from app.service.bearer_auth import has_token
from app.service.helpers import get_uuid
from app.service.password import Password

stats_router = APIRouter()


@stats_router.get("/", name="ideas:List")
async def ideas_get_all(*, session: Session = Depends(get_session), auth=Depends(has_token)):

    return {"ideas": "ok"}
