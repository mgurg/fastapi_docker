from fastapi import APIRouter, Depends

# from sqlmodel import Session, select
from sqlalchemy.orm import Session

from app.crud import cc_crud
from app.db import get_public_db
from app.schemas.responses import StandardResponse
from app.service.scheduler import scheduler
from app.service.tenants import alembic_upgrade_head

# from app.models.models import Accounts, SettingAddIn, StandardResponse
# from app.schemas.schemas import SettingBase

cc_router = APIRouter()


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


@cc_router.post("/markOrphanFiles", name="files:MarkOrphans")
def cc_migrate_all(*, db: Session = Depends(get_public_db)):

    db_companies = cc_crud.get_public_companies(db)

    processed = []
    for company in db_companies:
        processed.append(company.tenant_id)
        # # TODO: one by one
        # scheduler.run_job(alembic_upgrade_head, args=[company.tenant_id])  # id=company.tenant_id
        # processed.append(company.tenant_id)

    return processed
