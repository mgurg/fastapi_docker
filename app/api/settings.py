# from typing import list

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db

# from app.models.models import Accounts, SettingAddIn, StandardResponse
# from app.schemas.schemas import SettingBase
from app.service.bearer_auth import has_token

setting_router = APIRouter()


@setting_router.get("/", name="settings:list")  # response_model=list[SettingAddIn],
def setting_get_all(*, db: Session = Depends(get_db), setting_names: list[str] = Query(None), auth=Depends(has_token)):
    pass
    # if setting_names is not None:
    #     allowed_settings = ["idea_registration_mode", "issue_registration_email"]
    #     if not set(setting_names).issubset(allowed_settings):
    #         raise HTTPException(status_code=404, detail="Setting not allowed")

    #     db_setting = (
    #         db.execute(
    #             select(Setting).where(Setting.account_id == auth["account"]).where(Setting.entity.in_(setting_names))
    #         )
    #         .scalars()
    #         .all()
    #     )
    # else:
    #     db_setting = db.execute(select(Setting).where(Setting.account_id == auth["account"])).scalars().all()

    # if not db_setting:
    #     raise HTTPException(status_code=404, detail="Settings not found")

    # res = {}
    # for elt in db_setting:
    #     res[elt.entity] = elt.value

    # if setting_names is not None:
    #     for status in setting_names:
    #         res.setdefault(status, None)

    # return res
