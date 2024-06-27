from loguru import logger
from sqlalchemy import text

from app.config import get_settings
from app.db import engine
from app.storage.storage_interface import StorageInterface
from app.storage.storage_service_provider import get_storage_provider

settings = get_settings()

def check_required_tables() -> set:
    required_tables = {"public_users", "public_companies"}
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """)
            )

            existing_tables = {row['table_name'] for row in result.mappings()}

            return required_tables - existing_tables
    except Exception as err:
        logger.exception("Database table check failed: {}", err)
        return required_tables  # Retu

def test_db() -> dict[str, str]:
    missing_tables = check_required_tables()
    if not missing_tables:
        return {"db": "healthy"}
    else:
        return {"db": "unhealthy"}


def test_storage(storage_provider: StorageInterface) -> dict[str, str]:
    try:
        test_url = storage_provider.get_url("healthcheck_test_object", expiration=10)
        if test_url:
            return {"storage": "healthy"}
        else:
            return {"storage": "unhealthy"}
    except Exception as err:
        logger.exception("Storage check failed: {}", err)
        return {"storage": "unhealthy"}


def run_healthcheck() -> dict[str, str]:
    db_status = test_db()
    storage_provider = get_storage_provider()
    storage_status = test_storage(storage_provider)

    overall_status = (
        "ALIVE" if all(status == "healthy" for status in [db_status["db"], storage_status["storage"]]) else "DEGRADED"
    )

    return {"status": overall_status, **db_status, **storage_status}
