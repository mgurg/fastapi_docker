import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings


class Settings(BaseSettings):
    environment: str = os.getenv("WORKING_ENVIRONMENT", "dev")
    s3_region: str = os.getenv("AWS_S3_DEFAULT_REGION")
    s3_access_key: str = os.getenv("AWS_S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
    s3_bucket_name: str = os.getenv("AWS_S3_BUCKET")

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        env_file = ".env"


@lru_cache()
def get_settings() -> BaseSettings:
    return Settings()
