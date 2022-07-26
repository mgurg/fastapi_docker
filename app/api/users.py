from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import crud_users
from app.db import get_db

user_router = APIRouter()


@user_router.get("/")
async def user_get_all(*, db: Session = Depends(get_db)):
    db_user = crud_users.get_users(db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_user


@user_router.post("/")  # , response_model=User
def read_user(*, db: Session = Depends(get_db)):
    return crud_users.create_user(db)
