# project/tests/conftest.py

import argparse
import os
import warnings

# from starlette.testclient import TestClient
import alembic
import alembic.config  # pylint: disable=E0401
import alembic.migration  # pylint: disable=E0401
import alembic.runtime.environment  # pylint: disable=E0401
import alembic.script  # pylint: disable=E0401
import alembic.util  # pylint: disable=E0401
import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from app.config import Settings
from app.db import get_db
from app.main import app
from app.service.tenants import alembic_upgrade_head, tenant_create
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# def get_settings_override():
#     return Settings(testing=1, TEST_SQLALCHEMY_DATABASE_URI='os.environ.get("DATABASE_TEST_URL")')


# @pytest.fixture
# def aws_credentials():
#     """Mocked AWS Credentials for moto."""
#     os.environ["AWS_ACCESS_KEY_ID"] = "testing"
#     os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
#     os.environ["AWS_SECURITY_TOKEN"] = "testing"
#     os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"

    # tenant_create("a")
    alembic_upgrade_head("a")
    yield
    # alembic.command.downgrade(config, "base")


@pytest.fixture(name="session")
def session_fixture():
    load_dotenv("./app/.env")
    DEFAULT_DATABASE_USER = os.getenv("DB_USERNAME")
    DEFAULT_DATABASE_HOSTNAME: str = os.getenv("DB_HOST")
    DEFAULT_DATABASE_DB: str = os.getenv("DB_DATABASE")
    DEFAULT_DATABASE_USER: str = os.getenv("DB_USERNAME")
    DEFAULT_DATABASE_PASSWORD: str = os.getenv("DB_PASSWORD")

    engine = create_engine(
        f"postgresql+psycopg2://{DEFAULT_DATABASE_USER}:{DEFAULT_DATABASE_PASSWORD}@{DEFAULT_DATABASE_HOSTNAME}:5438/{DEFAULT_DATABASE_DB}",
        echo=True,
        pool_pre_ping=True,
        pool_recycle=280,
    )
    schema_translate_map = dict(tenant="a")
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    # def get_auth_override():
    #     return {"user": 1, "account": 2}

    app.dependency_overrides[get_db] = get_session_override
    # app.dependency_overrides[has_token] = get_auth_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
