# fastapi_docker/app/config.py

import logging
import os
from functools import lru_cache

from pydantic import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):

    environment: str = os.getenv("APP_ENV")

    s3_region: str = os.getenv("AWS_DEFAULT_REGION")
    s3_access_key: str = os.getenv("AWS_S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
    s3_bucket_name: str = os.getenv("AWS_S3_BUCKET")
    s3_bucket_region: str = os.getenv("AWS_S3_DEFAULT_REGION")

    sentry_dsn: str = os.getenv("SENTRY_DSN")

    # if environment != "test":
    #     secrets = get_secret()

    #     db_host: str = os.getenv("DB_HOST", f'{secrets["host"]}')
    #     db_port: str = os.getenv("DB_PORT", f'{secrets["port"]}')
    #     db_name: str = os.getenv("DB_DATABASE", f'{secrets["db_name"]}')
    #     db_user: str = os.getenv("DB_USERNAME", f'{secrets["username"]}')
    #     db_password: str = os.getenv("DB_PASSWORD", f'{secrets["password"]}')
    # else:
    db_host: str = os.getenv("DB_HOST")
    db_port: str = os.getenv("DB_PORT")
    db_name: str = os.getenv("DB_DATABASE")
    db_user: str = os.getenv("DB_USERNAME")
    db_password: str = os.getenv("DB_PASSWORD")

    email_labs_app_key: str = os.getenv("EMAIL_LABS_APP_KEY")
    email_labs_secret_key: str = os.getenv("EMAIL_LABS_APP_KEY")
    email_smtp: str = os.getenv("EMAIL_LABS_SMTP")
    email_sender: str = os.getenv("EMAIL_LABS_SENDER")
    email_dev: str = os.getenv("EMAIL_DEV")

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        env_file = ".env"


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
