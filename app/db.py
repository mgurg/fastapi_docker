from contextlib import contextmanager
from functools import lru_cache

import sqlalchemy as sa
from fastapi import Depends, Request
from loguru import logger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, declarative_base

from app.config import get_settings
from app.models.shared_models import PublicCompany

settings = get_settings()

DEFAULT_DATABASE_USER = settings.DEFAULT_DATABASE_USER
DEFAULT_DATABASE_PASSWORD = settings.DEFAULT_DATABASE_PASSWORD
DEFAULT_DATABASE_HOSTNAME = settings.DEFAULT_DATABASE_HOSTNAME
DEFAULT_DATABASE_PORT = settings.DEFAULT_DATABASE_PORT
DEFAULT_DATABASE_DB = settings.DEFAULT_DATABASE_DB
# SQLALCHEMY_DATABASE_URL = settings.DEFAULT_SQLALCHEMY_DATABASE_URI


# SQLALCHEMY_DATABASE_URL = PostgresDsn.build(
#     scheme="postgresql",
#     user=settings.DEFAULT_DATABASE_USER,
#     password=settings.DEFAULT_DATABASE_PASSWORD,
#     host=settings.DEFAULT_DATABASE_HOSTNAME,
#     port=5432,
#     path=settings.DEFAULT_DATABASE_DB,
# )

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DEFAULT_DATABASE_USER}:{DEFAULT_DATABASE_PASSWORD}@{DEFAULT_DATABASE_HOSTNAME}:5432/{DEFAULT_DATABASE_DB}"
echo = False
if settings.ENVIRONMENT != "PRD":
    print(SQLALCHEMY_DATABASE_URL)
    echo = True

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=echo, pool_pre_ping=True, pool_recycle=280)

# print(SQLALCHEMY_DATABASE_URL)

metadata = sa.MetaData(schema="tenant")
Base = declarative_base(metadata=metadata)


class TenantNotFoundError(Exception):
    def __init__(self, id):
        self.message = "Tenant %s not found!" % str(id)
        super().__init__(self.message)


@lru_cache()
def get_tenant(request: Request) -> PublicCompany:
    try:
        # host_without_port = request.headers["host"].split(":", 1)[0] # based on domain: __abc__.domain.com
        host_without_port = request.headers.get("tenant")  # based on tenant header: abc

        if host_without_port is None:
            return None

        with with_db(None) as db:
            tenant = db.execute(
                select(PublicCompany).where(PublicCompany.tenant_id == host_without_port)
            ).scalar_one_or_none()

        if tenant is None:
            # raise TenantNotFoundError(host_without_port)
            return None
    except Exception as e:
        print(e)
    return tenant


def get_db(tenant: PublicCompany = Depends(get_tenant)):
    if tenant is None:
        yield None

    with with_db(tenant.tenant_id) as db:
        yield db


def get_public_db():
    with with_db("public") as db:
        yield db
    # --------------------


@contextmanager
def with_db(tenant_schema: str | None):
    if tenant_schema:
        schema_translate_map = dict(tenant=tenant_schema)
    else:
        schema_translate_map = None

    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    try:
        db = Session(autocommit=False, autoflush=False, bind=connectable)
        yield db
    except Exception as e:
        logger.error(e)
        print("ERRRR: " + tenant_schema)
    finally:
        db.close()
