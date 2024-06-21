from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import SettingNotification, SettingUser, User


# GENERAL
# def get_general_settings_by_names(db: Session, user_id: int, names: list[str]) -> Sequence[SettingUser]:
#     query = select(SettingUser).where(SettingUser.user_id == user_id).where(SettingUser.name.in_(names))
#
#     result = db.execute(query)
#
#     return result.scalars().all()


# def get_user_general_setting_by_name(db: Session, user_id: int, name: str) -> SettingUser:
#     query = select(SettingUser).where(SettingUser.user_id == user_id).where(SettingUser.name == name)
#
#     result = db.execute(query)
#
#     return result.scalar_one_or_none()


# def create_user_setting(db: Session, data: dict) -> SettingUser:
#     new_setting = SettingUser(**data)
#     db.add(new_setting)
#     db.commit()
#     db.refresh(new_setting)
#
#     return new_setting


# def update_user_setting(db: Session, db_setting: SettingUser, update_data: dict) -> SettingUser:
#     for key, value in update_data.items():
#         setattr(db_setting, key, value)
#
#     db.add(db_setting)
#     db.commit()
#     db.refresh(db_setting)
#
#     return db_setting


#  NOTIFICATIONS
# def get_notification_settings_by_user_id(db: Session, user_id: int) -> SettingNotification:
#     query = select(SettingNotification).where(SettingNotification.user_id == user_id)
#
#     result = db.execute(query)
#
#     return result.scalar_one_or_none()


# def get_users_for_sms_notification(db: Session, notification_level: str):
#     query = (
#         select(User.phone, SettingNotification.sms_notification_level)
#         .where(SettingNotification.sms_notification_level == notification_level)
#         .outerjoin(User, User.id == SettingNotification.user_id)
#     )
#
#     result = db.execute(query)
#
#     return result.all()


# def get_users_for_email_notification(db: Session, notification_level: str):
#     query = (
#         select(User.email, SettingNotification.email_notification_level)
#         .where(SettingNotification.email_notification_level == notification_level)
#         .outerjoin(User, User.id == SettingNotification.user_id)
#     )
#
#     result = db.execute(query)
#
#     return result.all()


def get_users_list_for_email_notification(
    db: Session, notification_level: str, user_id: int | None = None
) -> list[User]:
    query = (
        select(User.id, User.email, User.first_name, User.last_name)
        .select_from(SettingNotification)
        .where(SettingNotification.email_notification_level == notification_level)
        .outerjoin(User, User.id == SettingNotification.user_id)
    )

    if user_id:
        query = query.where(User.id == user_id)

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
