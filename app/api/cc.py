from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.crud import cc_crud, crud_files, crud_users
from app.db import engine, get_db, get_public_db
from app.schemas.responses import StandardResponse
from app.service.notification_email import EmailNotification
from app.service.scheduler import scheduler
from app.service.tenants import alembic_upgrade_head

settings = get_settings()

cc_router = APIRouter()


@cc_router.get("/create")
def read_item(schema: str):
    # tenant_create(schema)
    # alembic_upgrade_head(schema)
    return {"schema": schema}


@cc_router.get("/manual_test", name="")
def cc_manual_test(*, db: Session = Depends(get_db)):
    db_user = crud_users.get_user_by_id(db, 1)

    email = EmailNotification()
    email.send_admin_registration(db_user, "/activate/123")

    return {"ok": True}


@cc_router.get("/check_revision")
def check_revision(schema: str):
    # with with_db(schema) as db:
    #     context = MigrationContext.configure(db.connection())
    #     script = alembic.script.ScriptDirectory.from_config(alembic_config)
    #     if context.get_current_revision() != script.get_current_head():
    return {"ok": True}


@cc_router.post("/mark_orphan_files", name="files:MarkOrphans")
def cc_mark_orphan_files(*, public_db: Session = Depends(get_public_db)):
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
def cc_get_all(*, db: Session = Depends(get_public_db)):
    db_companies = cc_crud.get_public_companies(db)

    return db_companies


@cc_router.post("/", name="migrate:All")
def cc_migrate_all(*, db: Session = Depends(get_public_db)):
    db_companies = cc_crud.get_public_companies(db)

    processed = []
    for company in db_companies:
        # TODO: one by one
        scheduler.run_job(alembic_upgrade_head, args=[company.tenant_id])  # id=company.tenant_id
        processed.append(company.tenant_id)

    return processed


@cc_router.post("/{tenant_id}", response_model=StandardResponse, name="migrate:One")
def cc_migrate_one(*, db: Session = Depends(get_public_db), tenant_id: str):
    scheduler.add_job(alembic_upgrade_head, args=[tenant_id])  # , id="tenant_id"

    return {"ok": True}
