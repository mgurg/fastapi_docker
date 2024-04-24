import time
from contextlib import contextmanager
from functools import lru_cache
from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, Request
from loguru import logger
from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base

from app.config import get_settings
from app.models.shared_models import PublicCompany

settings = get_settings()

DEFAULT_DB_USER = settings.DEFAULT_DATABASE_USER
DEFAULT_DB_PASS = settings.DEFAULT_DATABASE_PASSWORD
DEFAULT_DB_HOST = settings.DEFAULT_DATABASE_HOSTNAME
DEFAULT_DB_PORT = settings.DEFAULT_DATABASE_PORT
DEFAULT_DB = settings.DEFAULT_DATABASE_DB
# SQLALCHEMY_DB_URL = settings.DEFAULT_SQLALCHEMY_DATABASE_URI


# SQLALCHEMY_DB_URL = PostgresDsn.build(
#     scheme="postgresql",
#     user=settings.DEFAULT_DATABASE_USER,
#     password=settings.DEFAULT_DATABASE_PASSWORD,
#     host=settings.DEFAULT_DATABASE_HOSTNAME,
#     port=5432,
#     path=settings.DEFAULT_DATABASE_DB,
# )

sql_performance_monitoring = False
if sql_performance_monitoring is True:
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())
        logger.debug("Start Query:")
        logger.debug("%s" % statement)

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        logger.debug("Query Complete!")
        logger.debug("Total Time: %f" % total)


SQLALCHEMY_DB_URL = f"postgresql+psycopg://{DEFAULT_DB_USER}:{DEFAULT_DB_PASS}@{DEFAULT_DB_HOST}:5432/{DEFAULT_DB}"
echo = False

if settings.ENVIRONMENT != "PRD":
    print(SQLALCHEMY_DB_URL)
    echo = False

# TODO: https://bitestreams.com/nl/blog/fastapi_sqlalchemy/
engine = create_engine(SQLALCHEMY_DB_URL, echo=echo, pool_pre_ping=True, pool_recycle=280)

# print(SQLALCHEMY_DB_URL)

metadata = sa.MetaData(schema="tenant")
Base = declarative_base(metadata=metadata)


class TenantNotFoundError(Exception):
    def __init__(self, tenant_name):
        self.message = "Tenant %s not found!" % str(tenant_name)
        super().__init__(self.message)


@lru_cache
def get_tenant(request: Request) -> PublicCompany | None:
    try:
        # host_without_port = request.headers["host"].split(":", 1)[0] # based on domain: __abc__.domain.com
        host_without_port = request.headers.get("tenant")  # based on tenant header: abc

        if host_without_port is None:
            return None

        with with_db(None) as db:
            query = select(PublicCompany).where(PublicCompany.tenant_id == host_without_port)

            result = db.execute(query)
            tenant = result.scalar_one_or_none()

        if tenant is None:
            # raise TenantNotFoundError(host_without_port)
            return None
    except Exception as e:
        print(e)
    return tenant


def get_db(tenant: Annotated[PublicCompany, Depends(get_tenant)]):
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
        schema_translate_map = {"tenant": tenant_schema}
    else:
        schema_translate_map = None

    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    try:
        db = Session(autocommit=False, autoflush=False, bind=connectable)
        yield db
    except Exception as e:
        logger.error(e)
        print("ERRRR: " + tenant_schema)
        raise
    finally:
        db.close()
