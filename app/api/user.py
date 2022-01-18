from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import Users

user_router = APIRouter()


@user_router.get("/users", name="user:Profile")
async def user_get_all(*, session: Session = Depends(get_session)):
    users = session.exec(select(Users)).all()
    return users
