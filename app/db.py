from contextlib import contextmanager, asynccontextmanager
from functools import lru_cache

import sqlalchemy as sa
from fastapi import Depends, Request
from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

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

# SQLALCHEMY_DATABASE_URL = settings.DEFAULT_SQLALCHEMY_DATABASE_URI
# SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DEFAULT_DATABASE_USER}:{DEFAULT_DATABASE_PASSWORD}@{DEFAULT_DATABASE_HOSTNAME}:5432/{DEFAULT_DATABASE_DB}"
# for async support
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DEFAULT_DATABASE_USER}:{DEFAULT_DATABASE_PASSWORD}@{DEFAULT_DATABASE_HOSTNAME}:5432/{DEFAULT_DATABASE_DB}"
print(f"SQLALCHEMY_DATABASE_URL {SQLALCHEMY_DATABASE_URL}")
# engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False, pool_pre_ping=True, pool_recycle=280)
# for async support
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, pool_pre_ping=True, pool_recycle=280)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# print(SQLALCHEMY_DATABASE_URL)

metadata = sa.MetaData(schema="tenant")
Base = declarative_base(metadata=metadata)

print(SQLALCHEMY_DATABASE_URL)


class TenantNotFoundError(Exception):
    def __init__(self, id):
        self.message = "Tenant %s not found!" % str(id)
        super().__init__(self.message)

# for async support
# added async
@lru_cache()
async def get_tenant(request: Request) -> PublicCompany:
    try:
        # host_without_port = request.headers["host"].split(":", 1)[0] # based on domain: __abc__.domain.com
        host_without_port = request.headers.get("tenant")  # based on tenant header: abc

        if host_without_port is None:
            return None

        async with with_db(None) as db:
            tenant = db.execute(
                select(PublicCompany).where(PublicCompany.tenant_id == host_without_port)
            ).scalar_one_or_none()

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


# @contextmanager
# def with_db(tenant_schema: str | None):
#     if tenant_schema:
#         schema_translate_map = dict(tenant=tenant_schema)
#     else:
#         schema_translate_map = None

#     connectable = engine.execution_options(schema_translate_map=schema_translate_map)
#     try:
#         db = Session(autocommit=False, autoflush=False, bind=connectable)
#         yield db
#     except Exception:
#         print("ERRRR: " + tenant_schema)
#     finally:
#         db.close()


# for async support
@asynccontextmanager
async def with_db(tenant_schema: str | None):
    if tenant_schema:
        schema_translate_map = dict(tenant=tenant_schema)
    else:
        schema_translate_map = None

    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    try:
        async with async_session(autocommit=False, autoflush=False, bind=connectable) as session:
            yield session
    except Exception:
        await session.rollback()
        print("ERRRR: " + tenant_schema)
    finally:
        await session.close()