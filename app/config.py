import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings

# print(PROJECT_DIR)


class Settings(BaseSettings):
    PROJECT_DIR = Path(__file__).parent.parent
    ENVIRONMENT: Literal["DEV", "PYTEST", "STG", "PRD"] = os.getenv("APP_ENV")

    # API
    REJESTR_IO_KEY: str = os.getenv("REJESTR_IO_KEY")

    # POSTGRESQL DEFAULT DATABASE
    DEFAULT_DATABASE_HOSTNAME: str = os.getenv("DB_HOST")
    DEFAULT_DATABASE_PORT: str = os.getenv("DB_PORT")
    DEFAULT_DATABASE_DB: str = os.getenv("DB_DATABASE")
    DEFAULT_DATABASE_USER: str = os.getenv("DB_USERNAME")
    DEFAULT_DATABASE_PASSWORD: str = os.getenv("DB_PASSWORD")

    DEFAULT_SQLALCHEMY_DATABASE_URI: str = ""

    # POSTGRESQL TEST DATABASE
    TEST_DATABASE_HOSTNAME: str = "postgres"
    TEST_DATABASE_USER: str = "postgres"
    TEST_DATABASE_PASSWORD: str = "postgres"
    TEST_DATABASE_PORT: str = "5432"
    TEST_DATABASE_DB: str = "postgres"
    # TEST_SQLALCHEMY_DATABASE_URI: str = ""
    TEST_SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_TEST_URL")

    # @validator("DEFAULT_SQLALCHEMY_DATABASE_URI")
    # def _assemble_default_db_connection(cls, v: str, values: dict[str, str]) -> str:
    #     return PostgresDsn.build(
    #         scheme="postgresql+psycopg2",
    #         user=values["DEFAULT_DATABASE_USER"],
    #         password=values["DEFAULT_DATABASE_PASSWORD"],
    #         host=values["DEFAULT_DATABASE_HOSTNAME"],
    #         port=values["DEFAULT_DATABASE_PORT"],
    #         path=f"/{values['DEFAULT_DATABASE_DB']}",
    #     )

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        env_file = ".env"


@lru_cache()
def get_settings() -> BaseSettings:
    return Settings()
