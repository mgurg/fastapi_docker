# project/tests/conftest.py

import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from starlette.testclient import TestClient

from app.config import get_settings
from app.main import create_application

# def get_settings_override():
#     return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(name="session")
def session_fixture():
    os.environ["environment"] = "test"
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# ------


@pytest.fixture(scope="module")
def test_app():
    # set up
    app = create_application()
    # app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:

        # testing
        yield test_client

    # tear down


# new
# @pytest.fixture(scope="module")
# def test_app_with_db():
#     # set up
#     app = create_application()
#     app.dependency_overrides[get_settings] = get_settings_override
#     register_tortoise(
#         app,
#         db_url=os.environ.get("DATABASE_TEST_URL"),
#         modules={"models": ["app.models.tortoise"]},
#         generate_schemas=True,
#         add_exception_handlers=True,
#     )
#     with TestClient(app) as test_client:

#         # testing
#         yield test_client

#     # tear down
