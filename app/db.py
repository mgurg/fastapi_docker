from config import get_settings
from sqlmodel import Session, create_engine

settings = get_settings()

host = settings.db_host
port = settings.db_port
database = settings.db_name
user = settings.db_username
password = settings.db_password

database = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}?charset=utf8"
# database = f"postgresql://{user}:{password}@{host}:5432/{database}?charset=utf8"

engine = create_engine(database, encoding="utf-8", echo=True, pool_pre_ping=True, pool_recycle=280)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    # SQLModel.metadata.create_all(engine)
    pass
