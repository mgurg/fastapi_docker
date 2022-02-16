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

file_router = APIRouter()


@file_router.get("/index", response_model=List[FileResponse], name="user:Profile")
async def file_get_all(*, session: Session = Depends(get_session)):
    files = session.exec(select(Files).where(Files.client_id == 2).where(Files.deleted_at == None)).all()
    return files


@file_router.get("/{uuid}", response_model=FileUrlResponse, name="user:Profile")
async def file_get_all(*, session: Session = Depends(get_session), uuid):
    file = session.exec(
        select(Files).where(Files.client_id == 2).where(Files.uuid == uuid).where(Files.deleted_at == None)
    ).one_or_none()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file = dict(file)
    file["url"] = "https://placeimg.com/500/300/nature?t=" + file["file_name"]

    return file
