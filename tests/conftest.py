# project/tests/conftest.py

import os
from pathlib import Path

# from starlette.testclient import TestClient
import alembic
import alembic.config  # pylint: disable=E0401
import alembic.migration  # pylint: disable=E0401
import alembic.runtime.environment  # pylint: disable=E0401
import alembic.script  # pylint: disable=E0401
import alembic.util  # pylint: disable=E0401
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import get_db, get_public_db
from app.main import app
from app.service.bearer_auth import has_token
from app.service.tenants import alembic_upgrade_head, tenant_create, tenant_remove

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

# ENV_PATH = Path(__file__).parent.parent / "app" / ".env.testing"

# load_dotenv("/home/mgur/Git/fastapi_docker/app/.env.testing")
DEFAULT_DATABASE_USER = os.getenv("DB_USERNAME")
DEFAULT_DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
DEFAULT_DATABASE_HOSTNAME = os.getenv("DB_HOST")
DEFAULT_DATABASE_PORT = os.getenv("DB_PORT")
DEFAULT_DATABASE_DB = os.getenv("DB_DATABASE")
URL = f"postgresql+psycopg2://{DEFAULT_DATABASE_USER}:{DEFAULT_DATABASE_PASSWORD}@{DEFAULT_DATABASE_HOSTNAME}:5432/{DEFAULT_DATABASE_DB}"

os.environ["ENVIRONMENT"] = "PYTEST"
os.environ["TESTING"] = str("1")
os.environ["SQLALCHEMY_WARN_20"] = "1"


def pytest_configure():
    print("Hello! 👋")
    logger.error("Hello ENV: " + os.getenv("TESTING"))
    logger.error("Hello ENV: " + os.getenv("ENVIRONMENT"))
    # logger.error("Hello ENV: " + os.getenv("EMAIL_DEV"))

    # tenant_create("test_fake_schema")


def pytest_unconfigure():
    print("Bye! 🏁")

    # print("Tenant  created")
    # alembic_upgrade_head("test_fake_schema", "head", URL)
    # print("Tenant B upgraded")
    # tenant_remove("b")


# @pytest.fixture(scope="module", autouse=True)
# def my_fixture():
#     # app.dependency_overrides[get_settings] = get_settings_override
#     os.environ["TESTING"] = "1"
#     os.environ["SQLALCHEMY_WARN_20"] = "1"
#     logger.info("INITIALIZATION ")
#     logger.error("TESTING ENV: ", os.environ.get("TESTING"))
#     # alembic_upgrade_head("a", "head", URL)
#     yield
#     logger.critical("TEAR DOWN")


# @pytest.fixture(scope="session")
# def apply_migrations():
#     logger.critical("e1")
#     warnings.filterwarnings("ignore", category=DeprecationWarning)
#     os.environ["TESTING"] = "1"
#     try:
#         # tenant_create("a")
#         alembic_upgrade_head("a", "head", "postgresql+psycopg2://postgres:postgres@192.166.219.228:5432/postgres")
#     except Exception as e:
#         print(e)
#         logger.critical("e2")
#     yield
#     # alembic.command.downgrade(config, "base")


@pytest.fixture(name="session")
def session_fixture():

    engine = create_engine(URL, echo=False, pool_pre_ping=True, pool_recycle=280)
    schema_translate_map = dict(tenant="fake_tenant_company_for_test_00000000000000000000000000000000")
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    def get_auth_override():
        return {"user_id": 1}

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[has_token] = get_auth_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="publicSession")
def public_session_fixture():

    engine = create_engine(URL, echo=False, pool_pre_ping=True, pool_recycle=280)
    schema_translate_map = dict(tenant="public")
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:
        yield session


@pytest.fixture(name="publicClient")
def public_client_fixture(publicSession: Session):
    def get_session_override():
        return publicSession

    def get_auth_override():
        return {"user_id": 1}

    app.dependency_overrides[get_public_db] = get_session_override
    app.dependency_overrides[has_token] = get_auth_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
