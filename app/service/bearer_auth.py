import base64

import pendulum
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.crud import crud_auth
from app.db import get_db

settings = get_settings()
security = HTTPBearer()


def is_base64(sb: str) -> bool:
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            decoded_token = base64.b64decode(sb).decode("utf-8")
            base64_token = crud_auth.generate_base64_token(decoded_token)
            # message_bytes = .encode("ascii")
            # base64_bytes = base64.b64encode(message_bytes)
            # base64_message = base64_bytes.decode("ascii")
            return base64_token == sb
        else:
            raise ValueError("Argument must be string")

    except Exception:
        return False


def has_token(*, db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    """
    Function that is used to validate the token in the case that it requires it
    """

    if db is None:
        raise HTTPException(status_code=401, detail="General DB Error, missing tenant?")

    token = credentials.credentials
    if token is None:
        raise HTTPException(status_code=401, detail="Missing auth token")

    db_user_data = crud_auth.get_tenant_user_by_auth_token(db, token)

    if db_user_data is not None:
        # user_id, account_id = db_user_data
        return {"user_id": db_user_data.id}

    if is_base64(token) and (db_user_data is None):
        base64_message = token
        base64_bytes = base64_message.encode("ascii")
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode("ascii")

        tenant_id, date = message.split(".")  # TODO: tenant_id

        dt = pendulum.from_format(date, "YYYY-MM-DD HH:mm:ss", tz="UTC")
        if dt.diff(pendulum.now("UTC")).in_seconds() < 1:
            raise HTTPException(status_code=401, detail="Anonymous token expired")

        return {"user_id": 0}

    raise HTTPException(status_code=401, detail="Incorrect auth token")


def is_app_owner(credentials: HTTPBasicCredentials = Depends(security)):
    token = credentials.credentials
    if token is None:
        raise HTTPException(status_code=401, detail="Missing auth token")

    if token == "123":
        return True

    return False


# def has_permission(*, session: Session = Depends(get_session), user_id, permission):
#     fields = [Users.id, Users.user_role_id, Users.account_id]
#     user_data = session.exec(
#         select(*fields).where(Users.id == user_id).where(Users.is_active == 1).where(Users.deleted_at == None)
#     ).one_or_none()
#     raise HTTPException(status_code=403, detail="Insufficient privileges")
