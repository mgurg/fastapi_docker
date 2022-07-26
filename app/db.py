from contextlib import contextmanager
from typing import Optional

import sqlalchemy as sa
from fastapi import Depends, Request
from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.shared_models import PublicCompany

settings = get_settings()

DEFAULT_DATABASE_USER = settings.DEFAULT_DATABASE_USER
DEFAULT_DATABASE_PASSWORD = settings.DEFAULT_DATABASE_PASSWORD
DEFAULT_DATABASE_HOSTNAME = settings.DEFAULT_DATABASE_HOSTNAME
DEFAULT_DATABASE_PORT = str(settings.DEFAULT_DATABASE_PORT)
db_database = settings.DEFAULT_DATABASE_DB

# SQLALCHEMY_DATABASE_URL = settings.DEFAULT_SQLALCHEMY_DATABASE_URI
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DEFAULT_DATABASE_USER}:{DEFAULT_DATABASE_PASSWORD}@{DEFAULT_DATABASE_HOSTNAME}:5438/{db_database}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, pool_pre_ping=True, pool_recycle=280)

# print(SQLALCHEMY_DATABASE_URL)

metadata = sa.MetaData(schema="tenant")
Base = declarative_base(metadata=metadata)


# def get_shared_metadata():
#     meta = MetaData()
#     for table in Base.metadata.tables.values():
#         if table.schema != "tenant":
#             table.tometadata(meta)
#     return meta


# def get_tenant_specific_metadata():
#     meta = MetaData(schema="tenant")
#     for table in Base.metadata.tables.values():
#         if table.schema == "tenant":
#             table.tometadata(meta)
#     return meta


class TenantNotFoundError(Exception):
    def __init__(self, id):
        self.message = "Tenant %s not found!" % str(id)
        super().__init__(self.message)


def get_tenant(req: Request) -> PublicCompany:
    try:
        host_without_port = req.headers["host"].split(":", 1)[0]
        print("Sending request to DB:", host_without_port)
        with with_db(None) as db:
            tenant = db.execute(
                select(PublicCompany).where(PublicCompany.tenant_id == host_without_port)
            ).scalar_one_or_none()

        if tenant is None:
            raise TenantNotFoundError(host_without_port)
    except Exception as e:
        print(e)
    return tenant


def get_db(tenant: PublicCompany = Depends(get_tenant)):
    # print("tenant.schema", tenant.schema)
    with with_db(tenant.tenant_id) as db:
        yield db


def get_public_db():
    with with_db("public") as db:
        yield db
    # --------------------


@contextmanager
def with_db(tenant_schema: Optional[str]):
    if tenant_schema:
        schema_translate_map = dict(tenant=tenant_schema)
    else:
        schema_translate_map = None

    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    try:
        db = Session(autocommit=False, autoflush=False, bind=connectable)
        yield db
    finally:
        db.close()
