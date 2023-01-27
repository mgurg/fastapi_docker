# from typing import list
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import crud_settings
from app.db import get_db
from app.schemas.requests import SettingNotificationIn
from app.schemas.responses import SettingNotificationResponse

# from app.models.models import Accounts, SettingAddIn, StandardResponse
# from app.schemas.schemas import SettingBase
from app.service.bearer_auth import has_token

setting_router = APIRouter()

# GENERAL
@setting_router.get("/", name="settings:list")  # response_model=list[SettingAddIn],
def setting_get_all(*, db: Session = Depends(get_db), setting_names: list[str] = Query(None), auth=Depends(has_token)):
    ...
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


# Notifications
@setting_router.get("/notifications/", response_model=SettingNotificationResponse, name="settings:notifications")
def setting_notification_get(*, db: Session = Depends(get_db), auth=Depends(has_token)):

    user_id = auth["user_id"]

    db_settings = crud_settings.get_notification_settings_by_user_id(db, user_id)

    if db_settings is None:
        raise HTTPException(status_code=404, detail="Notification setting not found")

    return db_settings


@setting_router.post("/notifications/", response_model=SettingNotificationResponse, name="settings:notifications")
def setting_notification_set(*, db: Session = Depends(get_db), setting: SettingNotificationIn, auth=Depends(has_token)):

    user_id = auth["user_id"]

    db_settings = crud_settings.get_notification_settings_by_user_id(db, user_id)

    if db_settings is None:
        setting_data = {
            "user_id": user_id,
            "sms_notification_level": setting.sms_notification_level,
            "email_notification_level": setting.email_notification_level,
            "created_at": datetime.now(timezone.utc),
        }

        db_settings = crud_settings.create_notification_setting(db, setting_data)
        return db_settings

    crud_settings.update_notification_setting(db, db_settings, setting.dict(exclude_unset=False))

    return db_settings
