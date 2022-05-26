from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db import get_session
from app.models.models import SettingAddIn, Settings, StandardResponse
from app.service.bearer_auth import has_token

setting_router = APIRouter()


@setting_router.get("/", name="settings:List")  # response_model=List[SettingAddIn],
async def setting_get_all(
    *, session: Session = Depends(get_session), setting_names: List[str] = Query(None), auth=Depends(has_token)
):

    if setting_names is not None:
        allowed_settings = ["idea_registration_mode", "issue_registration_email"]
        if not set(setting_names).issubset(allowed_settings):
            raise HTTPException(status_code=404, detail="Setting not allowed")

        db_setting = session.exec(
            select(Settings).where(Settings.account_id == auth["account"]).where(Settings.entity.in_(setting_names))
        ).all()
    else:
        db_setting = session.exec(select(Settings).where(Settings.account_id == auth["account"])).all()

    if not db_setting:
        raise HTTPException(status_code=404, detail="Settings not found")

    res = {}
    for elt in db_setting:
        res[elt.entity] = elt.value

    for status in setting_names:
        res.setdefault(status, None)

    return res


# @setting_router.get("/{setting_name}", name="settings:List")  # response_model=SettingAddIn,
# async def setting_get_all(*, session: Session = Depends(get_session), setting_name: str, auth=Depends(has_token)):

#     db_setting = session.exec(
#         select(Settings).where(Settings.account_id == auth["account"]).where(Settings.entity == setting_name)
#     ).one_or_none()

#     if not db_setting:
#         raise HTTPException(status_code=404, detail="Setting not found")

#     res = {}
#     # for elt in db_setting:
#     # res.setdefault(elt.entity, []).append(elt.value) //
#     res[db_setting.entity] = db_setting.value
#     # print(res)

#     return res


@setting_router.post("/", response_model=StandardResponse, name="settings:Add")
async def setting_add(*, session: Session = Depends(get_session), setting: SettingAddIn, auth=Depends(has_token)):

    allowed_settings = ["idea_registration_mode", "issue_registration_email"]

    res = SettingAddIn.from_orm(setting)

    if res.entity not in allowed_settings:
        raise HTTPException(status_code=404, detail="Setting not allowed")

    db_setting = session.exec(
        select(Settings).where(Settings.account_id == auth["account"]).where(Settings.entity == res.entity)
    ).first()

    if not db_setting:
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
    else:
        setting_data = setting.dict(exclude_unset=True)
        setting_data["updated_at"] = datetime.utcnow()
        for key, value in setting_data.items():
            setattr(db_setting, key, value)

        session.add(db_setting)
        session.commit()
        session.refresh(db_setting)

    return {"ok": True}
