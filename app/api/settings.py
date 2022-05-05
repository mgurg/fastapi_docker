from datetime import datetime, time, timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.db import get_session
from app.models.models import Settings, StandardResponse
from app.service.bearer_auth import has_token

setting_router = APIRouter()


@setting_router.get("/", name="settings:List")
async def ideas_get_all(*, session: Session = Depends(get_session), auth=Depends(has_token)):

    return {"setting": "ok"}
