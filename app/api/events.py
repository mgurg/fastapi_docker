from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import (
    FileResponse,
    Files,
    FileUrlResponse,
    StandardResponse,
    UserIndexResponse,
)
from app.service.password import Password

event_router = APIRouter()


@event_router.get("/index", response_model=List[FileResponse], name="user:Profile")
async def file_get_all(*, session: Session = Depends(get_session)):

    return "OK"
