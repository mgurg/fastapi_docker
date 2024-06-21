from fastapi import Depends
from loguru import logger

from app.config import get_settings
from app.db import engine
from app.storage.storage_interface import StorageInterface
from app.storage.storage_service_provider import get_storage_provider

settings = get_settings()


def test_storage(storage_provider: StorageInterface = Depends(get_storage_provider)) -> dict[str, str]:
    try:
        test_url = storage_provider.get_url("healthcheck_test_object", expiration=10)
        if test_url:
            return {"storage": "healthy"}
        else:
            return {"storage": "unhealthy"}
    except Exception as err:
        logger.exception("Storage check failed: {}", err)
        return {"storage": "unhealthy"}


def test_db() -> dict[str, str]:
    try:
        with engine.connect():
            return {"db": "healthy"}
    except Exception as err:
        logger.exception("Database connection failed: {}", err)
        raise err


def run_healthcheck(storage_provider: StorageInterface = Depends(get_storage_provider)) -> dict[str, str]:
    db_status = test_db()
    storage_status = test_storage(storage_provider)

    overall_status = (
        "ALIVE" if all(status == "healthy" for status in [db_status["db"], storage_status["storage"]]) else "DEGRADED"
    )

    return {"status": overall_status, **db_status, **storage_status}
