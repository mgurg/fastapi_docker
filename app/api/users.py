from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params, paginate
from sqlalchemy.orm import Session

from app.crud import crud_users
from app.db import get_db
from app.schemas.responses import UserIndexResponse

user_router = APIRouter()


@user_router.get("/", response_model=Page[UserIndexResponse])
async def user_get_all(*, db: Session = Depends(get_db), params: Params = Depends()):
    db_users = crud_users.get_users(db)
    return paginate(db_users, params)


@user_router.post("/")  # , response_model=User
def read_user(*, db: Session = Depends(get_db)):
    return crud_users.create_user(db)
