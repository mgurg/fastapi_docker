from faker import Faker
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import auth_router
from app.api.users import user_router
from app.db import get_db
from app.models.models import Book
from app.schemas.schemas import BookBase, StandardResponse
from app.service.tenants import alembic_upgrade_head, tenant_create

logger.add("./app/logs/logs.log", format="{time} - {level} - {message}", level="DEBUG", backtrace=False, diagnose=True)


# -------------------------------------------------------

origins = ["http://localhost", "http://localhost:8080", "*"]


def create_application() -> FastAPI:
    """
    Create base FastAPI app with CORS middlewares and routes loaded
    Returns:
        FastAPI: [description]
    """
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        auth_router,
        prefix="/auth",
        tags=["AUTH"],
    )

    app.include_router(
        user_router,
        prefix="/users",
        tags=["USER"],
    )

    return app


app = create_application()


@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting up and initializing app...")
    alembic_upgrade_head("public", "d6ba8c13303e")
    logger.info("🚀 Starting up and initializing app... DONE")


@app.get("/")
def read_root(request: Request):
    return {"Hello": "World"}


@app.get("/create")
def read_item(schema: str):
    tenant_create(schema)
    # alembic_upgrade_head(schema)
    return {
        "schema": schema,
    }


@app.get("/upgrade")
def upgrade_head(schema: str):
    # _has_table("a")
    alembic_upgrade_head(schema)
    return {"ok": True}


# Books CRUD


@app.get("/books")  # , response_model=List[BookBase]
# @logger.catch()
def index_books(*, session: Session = Depends(get_db)):
    db_book = session.execute(select(Book)).scalars().all()
    # if db_book is None:
    #     raise HTTPException(status_code=403, detail="Book not found")
    return db_book


@app.get("/books/{book_id}", response_model=BookBase)  #
def show_book(*, session: Session = Depends(get_db), book_id: int):
    db_book = session.execute(select(Book).where(Book.id == book_id)).scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.post("/books", response_model=BookBase)  #
def add_book(*, db: Session = Depends(get_db)):

    faker = Faker()

    new_book = Book(
        title=faker.catch_phrase(),
        author=faker.name(),
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@app.delete("/books/{book_id}", response_model=StandardResponse)  #
def delete_book(*, db: Session = Depends(get_db), book_id: int):

    db_book = db.execute(select(Book).where(Book.id == book_id)).scalar_one_or_none()
    db.delete(db_book)
    db.commit()

    return {"ok": True}
