# fastapi_docker/app/config.py

import logging
import os
from functools import lru_cache

from pydantic import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = os.getenv("WORKING_ENVIRONMENT", "dev")
    s3_region: str = os.getenv("AWS_S3_DEFAULT_REGION")
    s3_access_key: str = os.getenv("AWS_S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
    s3_bucket_name: str = os.getenv("AWS_S3_BUCKET")

    db_host: str = os.getenv("DB_HOST")
    db_port: str = os.getenv("DB_PORT")
    db_name: str = os.getenv("DB_DATABASE")
    db_user: str = os.getenv("DB_USERNAME")
    db_password: str = os.getenv("DB_PASSWORD")

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        env_file = ".env"


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()