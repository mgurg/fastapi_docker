from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from starlette.status import HTTP_204_NO_CONTENT

from app.api.service.setting_service import SettingsService
from app.models.models import User
from app.schemas.requests import SettingGeneralIn, SettingNotificationIn
from app.schemas.responses import SettingNotificationResponse
from app.service.bearer_auth import check_token

setting_test_router = APIRouter()

settingServiceDependency = Annotated[SettingsService, Depends()]
CurrentUser = Annotated[User, Depends(check_token)]


@setting_test_router.get("")
def get_general_settings(
    setting_service: settingServiceDependency, auth_user: CurrentUser, settings: Annotated[list[str], Query()] = None
):
    settings = setting_service.get_all(auth_user.id, settings)
    return settings


@setting_test_router.post("", status_code=HTTP_204_NO_CONTENT)
def set_general_setting(setting_service: settingServiceDependency, setting: SettingGeneralIn, auth_user: CurrentUser):
    setting_service.set(auth_user.id, setting)

    return None


@setting_test_router.get("/notifications", response_model=SettingNotificationResponse, name="settings:notifications")
def get_notification_level(setting_service: settingServiceDependency, auth_user: CurrentUser):
    notification_setting = setting_service.get_notification_settings(auth_user.id)
    return notification_setting


@setting_test_router.post("/notifications", response_model=SettingNotificationResponse, name="settings:notifications")
def set_notification_level(
    setting_service: settingServiceDependency, setting: SettingNotificationIn, auth_user: CurrentUser
):
    setting = setting_service.set_notification_settings(auth_user.id, setting)
    return setting


@setting_test_router.post("/user_lang/{language}", status_code=HTTP_204_NO_CONTENT)  # TODO breaking change, no body
def set_user_lang(
    setting_service: settingServiceDependency, language: Literal["de", "en-US", "fr", "pl"], auth_user: CurrentUser
):
    setting_service.set_language(auth_user.id, language)
    return None
