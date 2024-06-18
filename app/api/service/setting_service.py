from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from fastapi import Depends, HTTPException
from langcodes import standardize_tag
from pydantic import TypeAdapter
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.api.repository.SettingNotification import SettingNotificationRepo
from app.api.repository.SettingRepo import SettingRepo
from app.api.repository.SettingUser import SettingUserRepo
from app.api.repository.UserRepo import UserRepo
from app.models.models import SettingNotification, SettingUser
from app.schemas.requests import SettingGeneralIn, SettingNotificationIn

ALLOWED_LANGUAGES = Literal["de", "en-US", "fr", "pl"]
ALLOWED_SETTINGS: dict[str, Any] = {
    "idea_registration_mode": None,
    "issue_registration_email": None,
    "dashboard_show_intro": True,
}


class SettingsService:
    def __init__(
        self,
        setting_repo: Annotated[SettingRepo, Depends()],
        setting_user_repo: Annotated[SettingUserRepo, Depends()],
        setting_notification_repo: Annotated[SettingNotificationRepo, Depends()],
        user_repo: Annotated[UserRepo, Depends()],
    ) -> None:
        self.setting_repo = setting_repo
        self.setting_user_repo = setting_user_repo
        self.setting_notification_repo = setting_notification_repo
        self.user_repo = user_repo

    @staticmethod
    def get_type_adapter(value_type: str) -> TypeAdapter:
        type_map = {
            "str": str,
            "int": int,
            "bool": bool,
            "float": float,
        }
        if value_type in type_map:
            return TypeAdapter(type_map[value_type])
        raise ValueError(f"Unsupported value_type: {value_type}")

    def get_all(self, user_id: int, settings: list[str] = None):
        if user_id == 0:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Setting for anonymous user not exists!")

        if settings is None or not set(settings).issubset(ALLOWED_SETTINGS.keys()):
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Setting not allowed")

        db_settings = self.setting_user_repo.get_general_settings_by_names(user_id, settings)

        result = {}
        for setting in db_settings:
            try:
                adapter = self.get_type_adapter(setting.value_type)
                result[setting.name] = adapter.validate_python(setting.value)
            except ValueError as e:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

        for status in settings or []:
            result.setdefault(status, ALLOWED_SETTINGS[status])

        return result

    def set(self, user_id: int, setting: SettingGeneralIn) -> SettingUser:
        if setting.name not in ALLOWED_SETTINGS:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Setting `{setting.name}` not allowed")

        db_setting = self.setting_user_repo.get_user_setting_by_name(user_id, setting.name)

        if db_setting is None:
            data = {
                "user_id": user_id,
                "name": setting.name,
                "value": setting.value,
                "value_type": setting.type,
                "created_at": datetime.now(timezone.utc),
            }

            new_setting = self.setting_user_repo.create(**data)

            return new_setting

        data = {
            "value": setting.value,
            "value_type": setting.type,
            "prev_value": db_setting.value,
            "updated_at": datetime.now(timezone.utc),
        }

        self.setting_user_repo.update(db_setting.id, **data)
        db_setting = self.setting_user_repo.get_user_setting_by_name(user_id, setting.name)
        return db_setting

    def get_notification_settings(self, user_id: int) -> SettingNotification:
        db_settings = self.setting_notification_repo.get_by_user_id(user_id)

        if db_settings is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Notification setting not found")

        return db_settings

    def set_notification_settings(self, user_id: int, setting: SettingNotificationIn) -> SettingNotification:
        db_settings = self.setting_notification_repo.get_by_user_id(user_id)

        if db_settings is None:
            db_settings = self.setting_notification_repo.create(
                **{
                    "user_id": user_id,
                    "sms_notification_level": setting.sms_notification_level,
                    "email_notification_level": setting.email_notification_level,
                    "created_at": datetime.now(timezone.utc),
                }
            )
            return db_settings

        self.setting_notification_repo.update(
            db_settings.id,
            **{
                "sms_notification_level": setting.sms_notification_level,
                "email_notification_level": setting.email_notification_level,
                "updated_at": datetime.now(timezone.utc),
            },
        )

        return db_settings

    def set_language(self, user_id: int, language: str) -> None:
        self.user_repo.update(user_id, **{"lang": standardize_tag(language)})

        return None
