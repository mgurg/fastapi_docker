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


@cc_router.get("/", name="settings:List")  # response_model=List[SettingAddIn],
def cc_get_all(*, db: Session = Depends(get_public_db)):

    db_companies = cc_crud.get_public_companies(db)

    return db_companies


@cc_router.post("/", name="settings:List")  # response_model=List[SettingAddIn],
def cc_migrate_all(*, db: Session = Depends(get_public_db)):

    db_companies = cc_crud.get_public_companies(db)

    processed = []
    for company in db_companies:
        scheduler.add_job(alembic_upgrade_head, args=[company.tenant_id], id=company.tenant_id)
        processed.append(company.tenant_id)

    return processed


@cc_router.post("/{tenant_id}", response_model=StandardResponse)  # response_model=List[SettingAddIn],
def cc_migrate_one(*, db: Session = Depends(get_public_db), tenant_id: str):

    scheduler.add_job(alembic_upgrade_head, args=[tenant_id], id="tenant_id")

    return {"ok": True}
