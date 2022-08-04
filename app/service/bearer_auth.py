import base64

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models.models import User

settings = get_settings()
security = HTTPBearer()


def has_token(*, db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(security)):
    """
    Function that is used to validate the token in the case that it requires it
    """

    token = credentials.credentials
    if token is None:
        raise HTTPException(status_code=401, detail="Missing auth token")

    db_user_data = db.execute(select(User).where(User.auth_token == token)).scalar_one_or_none()

    if db_user_data is not None:
        # user_id, account_id = db_user_data
        return {"user_id": db_user_data.id}
    else:
        try:
            base64_message = token
            base64_bytes = base64_message.encode("ascii")
            message_bytes = base64.b64decode(base64_bytes)
            message = message_bytes.decode("ascii")

            tenant_id, date = message.split(".")  # TODO: tenant_id & date check

            # db_account = session.execute(select(Account).where(Account.company_id == company)).one_or_none()
            return {"user_id": 0}
        except Exception as e:
            print("error" + e)

    raise HTTPException(status_code=401, detail="Incorrect auth token")


# def has_permission(*, session: Session = Depends(get_session), user_id, permission):
#     fields = [Users.id, Users.user_role_id, Users.account_id]
#     user_data = session.exec(
#         select(*fields).where(Users.id == user_id).where(Users.is_active == 1).where(Users.deleted_at == None)
#     ).one_or_none()
#     raise HTTPException(status_code=403, detail="Insufficient privileges")
