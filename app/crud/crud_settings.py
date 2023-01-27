from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Setting, SettingNotification, User


# GENERAL
def get_general_settings_by_names(db: Session, user_id, names: list) -> Setting:

    query = select(Setting).where(Setting.user_id == user_id).where(Setting.entity.in_(names))

    result = db.execute(query)

    return result.scalar_one_or_none()


#  NOTIFICATIONS
def get_notification_settings_by_user_id(db: Session, user_id: int) -> SettingNotification:
    query = select(SettingNotification).where(SettingNotification.user_id == user_id)

    result = db.execute(query)

    return result.scalar_one_or_none()


def get_users_for_sms_notification(db: Session, notification_level: str):
    query = (
        select(User.phone, SettingNotification.sms_notification_level)
        .where(SettingNotification.sms_notification_level == notification_level)
        .outerjoin(User, User.id == SettingNotification.user_id)
    )

    result = db.execute(query)

    return result.all()


def get_users_for_email_notification(db: Session, notification_level: str):
    query = (
        select(User.email, SettingNotification.email_notification_level)
        .where(SettingNotification.email_notification_level == notification_level)
        .outerjoin(User, User.id == SettingNotification.user_id)
    )

    result = db.execute(query)

    return result.all()


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
