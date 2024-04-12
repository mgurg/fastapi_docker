from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.service.user_service import UserService

user_test_router = APIRouter()


@user_test_router.get("/{user_uuid}")  # response_model=UserIndexResponse
def user_get_one(user_service: Annotated[UserService, Depends()], user_uuid: str):
    user = user_service.get_user_by_uuid(UUID(user_uuid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
