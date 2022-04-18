from typing import List

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import Users

settings = get_settings()
security = HTTPBearer()


async def has_token(*, session: Session = Depends(get_session), credentials: HTTPBasicCredentials = Depends(security)):
    """
    Function that is used to validate the token in the case that it requires it
    """
    token = credentials.credentials
    if token is None:
        raise HTTPException(status_code=401, detail="Missing auth token")

    db_user_data = session.exec(select(Users.id, Users.account_id).where(Users.auth_token == token)).one_or_none()

    if db_user_data is not None:
        user_id, account_id = db_user_data
        return {"user": user_id, "account": account_id}
    else:
        raise HTTPException(status_code=401, detail="Incorrect auth token")


# async def has_permission(*, session: Session = Depends(get_session), user_id, permission):
#     fields = [Users.id, Users.user_role_id, Users.account_id]
#     user_data = session.exec(
#         select(*fields).where(Users.id == user_id).where(Users.is_active == 1).where(Users.deleted_at == None)
#     ).one_or_none()
#     raise HTTPException(status_code=403, detail="Insufficient privileges")


# async def details(
#     *, session: Session = Depends(get_session), credentials: HTTPBasicCredentials = Depends(security)
# ) -> List[int]:
#     """Returns (for authenticated User): user_id, user_role_id, account_id"""
#     token = credentials.credentials
#     if token is None:
#         raise HTTPException(status_code=401, detail="Missing auth token")

#     db_user_id = session.exec(select(Users.id).where(Users.auth_token == token)).one_or_none()
#     if db_user_id is None:
#         raise HTTPException(status_code=401, detail="Incorrect auth token")

#     fields = [Users.id, Users.user_role_id, Users.account_id]
#     user_data = session.exec(
#         select(*fields).where(Users.id == db_user_id).where(Users.is_active == 1).where(Users.deleted_at == None)
#     ).one_or_none()

#     user_id, user_role_id, account_id = user_data
#     return [user_id, user_role_id, account_id]
