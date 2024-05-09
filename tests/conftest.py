# project/tests/conftest.py

import os
import traceback
import warnings
from pathlib import Path

# from starlette.testclient import TestClient
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from fastapi_pagination.utils import FastAPIPaginationWarning
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from app.db import get_session, get_db
from app.main import app
from app.models.models import User
from app.service.bearer_auth import has_token

# def get_settings_override():
#     load_dotenv("./app/.env")
#     settings = Settings(
#         DEFAULT_DATABASE_HOSTNAME=os.getenv("DB_HOST"),
#         DEFAULT_DATABASE_PORT=os.getenv("DB_PORT"),
#         DEFAULT_DATABASE_DB=os.getenv("DB_DATABASE"),
#         DEFAULT_DATABASE_USER=os.getenv("DB_USERNAME"),
#         DEFAULT_DATABASE_PASSWORD=os.getenv("DB_PASSWORD"),
#     )
#     return settings
# return Settings(testing=1, TEST_SQLALCHEMY_DATABASE_URI='os.environ.get("TEST_SQLALCHEMY_DATABASE_URI")')

# @pytest.fixture
# def aws_credentials():
#     """Mocked AWS Credentials for moto."""
#     os.environ["AWS_ACCESS_KEY_ID"] = "testing"
#     os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
#     os.environ["AWS_SECURITY_TOKEN"] = "testing"
#     os.environ["AWS_SESSION_TOKEN"] = "testing"

ENV_PATH = Path(__file__).parent.parent / "app" / ".env"

load_dotenv(ENV_PATH)
DEFAULT_DATABASE_USER = os.getenv("DB_USERNAME")
DEFAULT_DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
DEFAULT_DATABASE_HOSTNAME = os.getenv("DB_HOST")
DEFAULT_DATABASE_PORT = os.getenv("DB_PORT")
DEFAULT_DATABASE_DB = os.getenv("DB_DATABASE")
URL = f"postgresql+psycopg://{DEFAULT_DATABASE_USER}:{DEFAULT_DATABASE_PASSWORD}@{DEFAULT_DATABASE_HOSTNAME}:5432/{DEFAULT_DATABASE_DB}"

os.environ["ENVIRONMENT"] = "PYTEST"
os.environ["APP_ENV"] = "PYTEST"
os.environ["TESTING"] = str("1")
warnings.simplefilter("ignore", FastAPIPaginationWarning)

POSTGRES_VERSION = "postgres:15.1"


def pytest_configure():
    print("Test is running... 🧪")
    logger.error("Hello ENV: " + os.getenv("TESTING"))
    logger.error("Hello ENV: " + os.getenv("ENVIRONMENT"))


# We bind this to session level to ensure it is only
# initialized once.
# https://github.com/search?q=PostgresContainer++path%3A**%2Fconftest.py+language%3APython&type=code&ref=advsearch
@pytest.fixture(scope="session")
def session_fixture():
    pg = PostgresContainer(POSTGRES_VERSION, driver="psycopg")
    # pg.volumes = {str('sql'): {"bind": "/data"}}

    current_dir = Path(__file__).resolve().parent
    root_dir = current_dir.parent.parent
    sql_dir = str(current_dir / "sql/users.sql")

    pg.with_volume_mapping(
        host=sql_dir,
        container="/docker-entrypoint-initdb.d/users.sql",
    )
    with pg as postgres_container:
        psql_url = postgres_container.get_connection_url()
        print(psql_url)
        engine = create_engine(postgres_container.get_connection_url())
        schema_translate_map = dict(tenant="fake_tenant_company_for_test_00000000000000000000000000000000")
        connectable = engine.execution_options(schema_translate_map=schema_translate_map)
        with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:
            yield session
@pytest.fixture(scope="session")
def db_fixture():
    pg = PostgresContainer(POSTGRES_VERSION, driver="psycopg")
    # pg.volumes = {str('sql'): {"bind": "/data"}}

    current_dir = Path(__file__).resolve().parent
    root_dir = current_dir.parent.parent
    sql_dir = str(current_dir / "sql/users.sql")

    pg.with_volume_mapping(
        host=sql_dir,
        container="/docker-entrypoint-initdb.d/users.sql",
    )
    with pg as postgres_container:
        psql_url = postgres_container.get_connection_url()
        print(psql_url)
        engine = create_engine(postgres_container.get_connection_url())
        schema_translate_map = dict(tenant="fake_tenant_company_for_test_00000000000000000000000000000000")
        connectable = engine.execution_options(schema_translate_map=schema_translate_map)
        with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:
            yield session

@pytest.fixture(name="client")
def client_fixture(db_fixture: Session, session_fixture: Session):
    def get_session_override():
        return session_fixture

    def get_db_override():
        return db_fixture

    def get_auth_override():
        return User(id=1)

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[has_token] = get_auth_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


#
#
# @pytest.fixture(name="session")
# def session_fixture():
#     engine = create_engine(URL, echo=False, pool_pre_ping=True, pool_recycle=280)
#     schema_translate_map = dict(tenant="fake_tenant_company_for_test_00000000000000000000000000000000")
#     connectable = engine.execution_options(schema_translate_map=schema_translate_map)
#     with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:
#         yield session

#


#


#
# @pytest.fixture(name="publicSession")
# def public_session_fixture():
#     engine = create_engine(URL, echo=False, pool_pre_ping=True, pool_recycle=280)
#     schema_translate_map = dict(tenant="public")
#     connectable = engine.execution_options(schema_translate_map=schema_translate_map)
#     with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:
#         yield session
#
#
# @pytest.fixture(name="publicClient")
# def public_client_fixture(publicSession: Session):
#     def get_session_override():
#         return publicSession
#
#     def get_auth_override():
#         return {"user_id": 1}
#
#     app.dependency_overrides[get_public_db] = get_session_override
#     app.dependency_overrides[has_token] = get_auth_override
#
#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()
