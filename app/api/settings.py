from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db import get_session
from app.models.models import SettingAddIn, Settings, StandardResponse
from app.service.bearer_auth import has_token

setting_router = APIRouter()


@setting_router.get("/", response_model=List[SettingAddIn], name="settings:List")
async def setting_get_all(*, session: Session = Depends(get_session), auth=Depends(has_token)):

    db_setting = session.exec(select(Settings).where(Settings.account_id == auth["account"])).all()

    if not db_setting:
        raise HTTPException(status_code=404, detail="Settings not found")

    return db_setting


@setting_router.get("/{setting_name}", response_model=SettingAddIn, name="settings:List")
async def setting_get_all(*, session: Session = Depends(get_session), setting_name: str, auth=Depends(has_token)):

    db_setting = session.exec(
        select(Settings).where(Settings.account_id == auth["account"]).where(Settings.entity == setting_name)
    ).one_or_none()

    if not db_setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    return db_setting


@setting_router.post("/", response_model=StandardResponse, name="settings:Add")
async def setting_add(*, session: Session = Depends(get_session), setting: SettingAddIn, auth=Depends(has_token)):

    allowed_settings = ["mode"]

    res = SettingAddIn.from_orm(setting)

    new_setting = Settings(
        account_id=auth["account"],
        entity=res.entity,
        value=res.value,
        value_type=res.value_type,
        created_at=datetime.utcnow(),
    )

    session.add(new_setting)
    session.commit()
    session.refresh(new_setting)

    return {"ok": True}
