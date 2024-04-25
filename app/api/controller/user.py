from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.service.user_service import UserService
from app.db import get_session
from app.models.models import User
from app.schemas.responses import UserIndexResponse
from app.service.bearer_auth import has_token

user_test_router = APIRouter()

# CurrentUser = Annotated[User, Depends(has_token)]
# UserDB = Annotated[Session, Depends(get_session)]


@user_test_router.get("/{user_uuid}", response_model=UserIndexResponse)
def user_get_one(user_service: Annotated[UserService, Depends()], user_uuid: str):
    user = user_service.get_user_by_uuid(UUID(user_uuid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
