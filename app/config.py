import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_DIR = Path(__file__).parent.parent
    ENVIRONMENT: Literal["DEV", "PYTEST", "STG", "PRD"] = os.getenv("APP_ENV")

    s3_region: str = os.getenv("AWS_DEFAULT_REGION")
    s3_access_key: str = os.getenv("AWS_S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
    s3_bucket_name: str = os.getenv("AWS_S3_BUCKET")
    s3_bucket_region: str = os.getenv("AWS_S3_DEFAULT_REGION")

    sentry_dsn: str = os.getenv("SENTRY_DSN")

    email_labs_app_key: str = os.getenv("EMAIL_LABS_APP_KEY")
    email_labs_secret_key: str = os.getenv("EMAIL_LABS_APP_KEY")
    email_smtp: str = os.getenv("EMAIL_LABS_SMTP")
    email_sender: str = os.getenv("EMAIL_LABS_SENDER")
    email_dev: str = os.getenv("EMAIL_DEV")

    # API
    REJESTR_IO_KEY: str = os.getenv("REJESTR_IO_KEY")
    GUS_KEY: str = os.getenv("GUS_API")
    GUS_API_DEV: str = os.getenv("GUS_API_DEV")

    # POSTGRESQL DEFAULT DATABASE
    DEFAULT_DATABASE_HOSTNAME: str = os.getenv("DB_HOST")
    DEFAULT_DATABASE_PORT: str = os.getenv("DB_PORT")
    DEFAULT_DATABASE_DB: str = os.getenv("DB_DATABASE")
    DEFAULT_DATABASE_USER: str = os.getenv("DB_USERNAME")
    DEFAULT_DATABASE_PASSWORD: str = os.getenv("DB_PASSWORD")

    DEFAULT_SQLALCHEMY_DATABASE_URI: str = os.getenv("DEFAULT_SQLALCHEMY_DATABASE_URI")

    # POSTGRESQL TEST DATABASE
    TEST_DATABASE_HOSTNAME: str = "postgres"
    TEST_DATABASE_USER: str = "postgres"
    TEST_DATABASE_PASSWORD: str = "postgres"
    TEST_DATABASE_PORT: str = "5432"
    TEST_DATABASE_DB: str = "postgres"
    # TEST_SQLALCHEMY_DATABASE_URI: str = ""
    TEST_SQLALCHEMY_DATABASE_URI: str = os.getenv("TEST_SQLALCHEMY_DATABASE_URI")

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        env_file = ".env"


@lru_cache()
def get_settings() -> BaseSettings:
    return Settings()
