from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from app.config import get_settings

metadata = MetaData()
Base = declarative_base(metadata=metadata)

settings = get_settings()

host = settings.db_host
port = str(settings.db_port)
database = settings.db_name
user = settings.db_user
password = settings.db_password

database = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}"
engine = create_engine(database, echo=False, pool_pre_ping=True, pool_recycle=280)


def get_session():
    with Session(engine, future=True) as session:
        yield session


def create_db_and_tables():
    # SQLModel.metadata.create_all(engine)
    pass
