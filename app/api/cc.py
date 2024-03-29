import traceback
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.crud import cc_crud, crud_files
from app.db import engine, get_public_db
from app.schemas.responses import StandardResponse
from app.service.bearer_auth import is_app_owner
from app.service.scheduler import scheduler
from app.service.tenants import alembic_upgrade_head

settings = get_settings()

cc_router = APIRouter()

PublicDB = Annotated[Session, Depends(get_public_db)]


@cc_router.get("/create")
def read_item(schema: str):
    # tenant_create(schema)
    # alembic_upgrade_head(schema)
    return {"schema": schema}


@cc_router.get("/check_revision")
def check_revision(schema: str):
    # with with_db(schema) as db:
    #     context = MigrationContext.configure(db.connection())
    #     script = alembic.script.ScriptDirectory.from_config(alembic_config)
    #     if context.get_current_revision() != script.get_current_head():
    return {"ok": True}


@cc_router.post("/mark_orphan_files", name="files:MarkOrphans")
def cc_mark_orphan_files(*, public_db: PublicDB, auth=Depends(is_app_owner)):
    db_companies = cc_crud.get_public_companies(public_db)

    processed = []
    for company in db_companies:
        connectable = engine.execution_options(schema_translate_map={"tenant": company.tenant_id})
        with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as db:
            orphaned_files_uuid = crud_files.get_orphaned_files(db)
            processed.append({company.tenant_id: orphaned_files_uuid})
        # # TODO: one by one
        # scheduler.run_job(alembic_upgrade_head, args=[company.tenant_id])  # id=company.tenant_id
        # processed.append(company.tenant_id)

    return processed


@cc_router.get("/", name="companies:List")
def cc_get_all(*, public_db: PublicDB, auth=Depends(is_app_owner)):
    db_companies = cc_crud.get_public_companies(public_db)

    return db_companies


@cc_router.post("/", name="migrate:All")
def cc_migrate_all(*, public_db: PublicDB, auth=Depends(is_app_owner)):
    db_companies = cc_crud.get_public_companies(public_db)

    processed = []
    for company in db_companies:
        # TODO: one by one
        scheduler.run_job(alembic_upgrade_head, args=[company.tenant_id])  # id=company.tenant_id
        processed.append(company.tenant_id)

    return processed


@cc_router.post("/{tenant_id}", response_model=StandardResponse, name="migrate:One")
def cc_migrate_one(*, public_db: PublicDB, tenant_id: str, auth=Depends(is_app_owner)):
    scheduler.add_job(alembic_upgrade_head, args=[tenant_id])  # , id="tenant_id"

    return {"ok": True}


@cc_router.delete("/{tenant_id}", response_model=StandardResponse, name="migrate:One")
def cc_delete_one(*, public_db: PublicDB, tenant_id: str, auth=Depends(is_app_owner)):
    print("Cleaning DB 🧹")

    connection = engine.connect()
    trans = connection.begin()
    try:
        connection.execute(text(f"DELETE FROM public.public_users WHERE tenant_id = '{tenant_id}';"))
        connection.execute(text(f"DELETE FROM public.public_companies  WHERE tenant_id = '{tenant_id}';"))
        connection.execute(text('DROP SCHEMA IF EXISTS "' + tenant_id + '" CASCADE;'))
        trans.commit()
    except Exception:
        traceback.print_exc()
        trans.rollback()
    print("Bye! 🫡")

    return {"ok": True}
