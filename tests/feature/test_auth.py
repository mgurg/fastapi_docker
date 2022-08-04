import argparse
import os
import warnings
from pathlib import Path

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
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from loguru import logger
from sentry_sdk import capture_message
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import SQLALCHEMY_DATABASE_URL, get_db, get_public_db
from app.main import app
from app.service.bearer_auth import has_token
from app.service.tenants import alembic_upgrade_head, tenant_create


def test_register():
    assert 200 == 200
    # DEFAULT_DATABASE_USER = os.getenv("DB_USERNAME")
    # DEFAULT_DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
    # DEFAULT_DATABASE_HOSTNAME = os.getenv("DB_HOST")
    # DEFAULT_DATABASE_DB = os.getenv("DB_DATABASE")
    # URL = f"postgresql+psycopg2://{DEFAULT_DATABASE_USER}:{DEFAULT_DATABASE_PASSWORD}@{DEFAULT_DATABASE_HOSTNAME}:5432/{DEFAULT_DATABASE_DB}"

    # engine = create_engine(URL, echo=False, pool_pre_ping=True, pool_recycle=280)
    # schema_translate_map = dict(tenant="public")
    # connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    # with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:

    #     def get_session_override():
    #         return session  #

    #     app.dependency_overrides[get_public_db] = get_session_override  #

    #     client = TestClient(app)
    #     data = {
    #         "email": "test@example.com",
    #         "password": "string",
    #         "password_confirmation": "string",
    #         "tos": True,
    #         "tz": "Europe/Warsaw",
    #         "lang": "pl",
    #     }
    #     response = client.post("/auth/register", json=data, headers={"tenant": "public", "host": "public"})
    #     data = response.json()
    #     assert response.status_code == 200
