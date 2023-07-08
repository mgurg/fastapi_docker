import time
from contextlib import asynccontextmanager

import sqlalchemy as sa
from fastapi import Depends, Request
from loguru import logger
from sqlalchemy import event, select
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# from sqlalchemy.orm import declarative_base
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

# for async support
engine = create_async_engine(SQLALCHEMY_DB_URL, echo=echo, pool_pre_ping=True, pool_recycle=280)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# print(SQLALCHEMY_DB_URL)

metadata = sa.MetaData(schema="tenant")
Base = declarative_base(metadata=metadata)


class TenantNotFoundError(Exception):
    def __init__(self, id):
        self.message = "Tenant %s not found!" % str(id)
        super().__init__(self.message)


# for async support
# added async
# @lru_cache()
async def get_tenant(request: Request) -> PublicCompany:
    try:
        # host_without_port = request.headers["host"].split(":", 1)[0] # based on domain: __abc__.domain.com
        host_without_port = request.headers.get("tenant")  # based on tenant header: abc

        if host_without_port is None:
            return None

        async with with_db(None) as db:
            query = select(PublicCompany).where(PublicCompany.tenant_id == host_without_port)
            result = await db.execute(query)

            tenant = result.scalar_one_or_none()

        if tenant is None:
            # raise TenantNotFoundError(host_without_port)
            return None
    except Exception as e:
        print(e)
    return tenant


# for async support
# added async
async def get_db(tenant: PublicCompany = Depends(get_tenant)):
    if tenant is None:
        yield None

    async with with_db(tenant.tenant_id) as db:
        yield db


# for async support
# added async
async def get_public_db():
    async with with_db("public") as db:
        yield db
    # --------------------


# for async support
@asynccontextmanager
async def with_db(tenant_schema: str | None):
    if tenant_schema:
        schema_translate_map = {"tenant": tenant_schema}
    else:
        schema_translate_map = None

    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    try:
        async with async_session(autocommit=False, autoflush=False, bind=connectable) as session:
            yield session
    except Exception as e:
        logger.error(e)
        await session.rollback()
        print("ERRRR: " + tenant_schema)
    finally:
        await session.close()
