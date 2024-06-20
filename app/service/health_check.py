from loguru import logger
from app.config import get_settings
from app.db import engine
from app.storage.s3 import s3_client

settings = get_settings()

def test_db() -> dict[str, str]:
    try:
        with engine.connect():
            return {"db": "healthy"}
    except Exception as err:
        logger.exception("Database connection failed: {}", err)
        raise err

def test_storage() -> dict[str, str]:
    try:
        s3_client.head_bucket(Bucket=settings.s3_bucket_name)
        return {"storage": "healthy"}
    except Exception as err:
        logger.exception("S3 storage check failed: {}", err)
        raise err

def run_healthcheck() -> dict[str, str]:
    db_status = test_db()
    storage_status = test_storage()
    return {"status": "ALIVE", **db_status, **storage_status}
