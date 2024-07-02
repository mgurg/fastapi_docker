# from typing import list
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.models import User
from app.service.bearer_auth import has_token

setting_router = APIRouter()

CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[Session, Depends(get_db)]


# GENERAL
# @setting_router.get("/", name="setting:read")
# def setting_get_all(*, db: UserDB, auth_user: CurrentUser, settings: Annotated[list[str], Query()] = None):
#     user_id = auth_user.id
#
#     if user_id == 0:
#         raise HTTPException(status_code=404, detail="Setting for anonymous user not exists!")
#
#     if settings is None or not set(settings).issubset(allowed_settings.keys()):
#         raise HTTPException(status_code=404, detail="Setting not allowed")
#
#     db_settings = crud_settings.get_general_settings_by_names(db, user_id, settings)
#
#     result = {}
#     for elt in db_settings:
#         result[elt.name] = parse_obj_as(elt.value_type, elt.value)
#
#     if settings is not None:
#         for status in settings:
#             result.setdefault(status, allowed_settings[status])
#
#     return result


# @setting_router.post("/", name="setting:add")
# def setting_set_one(*, db: UserDB, setting: SettingGeneralIn, auth_user: CurrentUser):
#     user_id = auth_user.id
#
#     db_setting = crud_settings.get_user_general_setting_by_name(db, user_id, setting.name)
#
#     if db_setting is None:
#         data = {
#             "user_id": user_id,
#             "name": setting.name,
#             "value": setting.value,
#             "value_type": setting.type,
#             "created_at": datetime.now(timezone.utc),
#         }
#
#         new_setting = crud_settings.create_user_setting(db, data)
#
#         return new_setting
#
#     data = {
#         "value": setting.value,
#         "value_type": setting.type,
#         "prev_value": db_setting.value,
#         "updated_at": datetime.now(timezone.utc),
#     }
#
#     updated_setting = crud_settings.update_user_setting(db, db_setting, data)
#     return updated_setting


# Notifications
# @setting_router.get("/notifications/", response_model=SettingNotificationResponse, name="settings:notifications")
# def setting_notification_get(*, db: UserDB, auth_user: CurrentUser):
#     user_id = auth_user.id
#
#     db_settings = crud_settings.get_notification_settings_by_user_id(db, user_id)
#
#     if db_settings is None:
#         raise HTTPException(status_code=404, detail="Notification setting not found")
#
#     return db_settings


# @setting_router.post("/notifications/", response_model=SettingNotificationResponse, name="settings:notifications")
# def setting_notification_set(*, db: UserDB, setting: SettingNotificationIn, auth_user: CurrentUser):
#     user_id = auth_user.id
#
#     db_settings = crud_settings.get_notification_settings_by_user_id(db, user_id)
#
#     if db_settings is None:
#         setting_data = {
#             "user_id": user_id,
#             "sms_notification_level": setting.sms_notification_level,
#             "email_notification_level": setting.email_notification_level,
#             "created_at": datetime.now(timezone.utc),
#         }
#
#         db_settings = crud_settings.create_notification_setting(db, setting_data)
#         return db_settings
#
#     crud_settings.update_notification_setting(db, db_settings, setting.model_dump(exclude_unset=False))
#
#     return db_settings


# LANG
# @setting_router.post("/user_lang/", response_model=StandardResponse, name="settings:notifications")
# def setting_user_lang(*, db: UserDB, lang: SettingUserLanguage, auth_user: CurrentUser):
#     if lang.code not in ["de", "en-US", "fr", "pl"]:
#         raise HTTPException(status_code=404, detail="Language code setting invalid")
#
#     db_user = crud_users.get_user_by_id(db, auth_user.id)
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     crud_users.update_user(db, db_user, {"lang": standardize_tag(lang.code)})
#
#     return {"ok": True}
