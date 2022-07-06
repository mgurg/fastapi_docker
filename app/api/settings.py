from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

# from sqlmodel import Session, select
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.model.model import Settings

# from app.models.models import Accounts, SettingAddIn, StandardResponse
from app.schema.schema import SettingBase
from app.service.bearer_auth import has_token

setting_router = APIRouter()


@setting_router.get("/", name="settings:List")  # response_model=List[SettingAddIn],
async def setting_get_all(
    *, session: Session = Depends(get_session), setting_names: List[str] = Query(None), auth=Depends(has_token)
):

    # ------
    # heroes = session.execute(select(Settings)).scalars().first()
    # print(SettingBase.from_orm(heroes))

    # query = session.query(Settings).first()
    # b1_schema = SettingBase.from_orm(query)
    # print(b1_schema.json())

    # ------
    if setting_names is not None:
        allowed_settings = ["idea_registration_mode", "issue_registration_email"]
        if not set(setting_names).issubset(allowed_settings):
            raise HTTPException(status_code=404, detail="Setting not allowed")

        db_setting = (
            session.execute(
                select(Settings)
                .where(Settings.account_id == auth["account"])
                .where(Settings.entity.in_(setting_names))
            )
            .scalars()
            .all()
        )
    else:
        db_setting = session.execute(select(Settings).where(Settings.account_id == auth["account"])).scalars().all()

    if not db_setting:
        raise HTTPException(status_code=404, detail="Settings not found")

    res = {}
    for elt in db_setting:
        res[elt.entity] = elt.value

    if setting_names is not None:
        for status in setting_names:
            res.setdefault(status, None)

    return res


# @setting_router.get("/board/", name="settings:BoardUrl")  # response_model=SettingAddIn,
# async def setting_get_all(*, session: Session = Depends(get_session), auth=Depends(has_token)):

#     db_board = session.exec(select(Accounts.company_id).where(Accounts.account_id == auth["account"])).one_or_none()

#     if not db_board:
#         raise HTTPException(status_code=404, detail="Board not found")

#     return db_board


# @setting_router.post("/", response_model=StandardResponse, name="settings:Add")
# async def setting_add(*, session: Session = Depends(get_session), settings: List[SettingAddIn]):
#     # auth=Depends(has_token)
#     allowed_settings = ["idea_registration_mode", "issue_registration_email"]

#     for setting in settings:
#         res = SettingAddIn.from_orm(setting)

#         if res.entity not in allowed_settings:
#             raise HTTPException(status_code=404, detail=f"Setting {res.entity} - {res.value} is not allowed")

#         db_setting = session.exec(
#             select(Settings).where(Settings.account_id == 2).where(Settings.entity == res.entity)
#         ).first()

#         if not db_setting:
#             new_setting = Settings(
#                 account_id=2,
#                 entity=res.entity,
#                 value=res.value,
#                 value_type=res.value_type,
#                 created_at=datetime.utcnow(),
#             )

#             session.add(new_setting)
#             session.commit()
#             session.refresh(new_setting)
#         else:
#             setting_data = setting.dict(exclude_unset=True)
#             setting_data["updated_at"] = datetime.utcnow()
#             for key, value in setting_data.items():
#                 setattr(db_setting, key, value)

#             session.add(db_setting)
#             session.commit()
#             session.refresh(db_setting)

#     return {"ok": True}
