from sqlmodel import Session, create_engine

from app.config import get_settings

settings = get_settings()

host = settings.db_host
port = str(settings.db_port)
database = settings.db_name
user = settings.db_user
password = settings.db_password

database = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}"
engine = create_engine(database, echo=False, pool_pre_ping=True, pool_recycle=280)
print(database)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    # SQLModel.metadata.create_all(engine)
    pass
