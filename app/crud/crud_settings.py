from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import SettingNotification


def get_notification_settings_by_user_id(db: Session, user_id: int) -> SettingNotification:
    query = select(SettingNotification).where(SettingNotification.user_id == user_id)

    result = db.execute(query)

    return result.scalar_one_or_none()


def create_notification_setting(db: Session, data: dict) -> SettingNotification:
    new_setting_notification = SettingNotification(**data)
    db.add(new_setting_notification)
    db.commit()
    db.refresh(new_setting_notification)

    return new_setting_notification


def update_notification_setting(db: Session, db_setting: SettingNotification, update_data: dict) -> SettingNotification:
    for key, value in update_data.items():
        setattr(db_setting, key, value)

    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)

    return db_setting
