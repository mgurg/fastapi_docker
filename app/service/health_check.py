from loguru import logger

from app.config import get_settings
from app.db import engine
from app.storage.aws_s3 import s3_client

settings = get_settings()


def test_db():
    try:
        with engine.connect():
            return {"db": "healthy"}
    except Exception as err:
        logger.exception(err)
        raise err


def test_storage():
    try:
        s3_client.head_bucket(Bucket=settings.s3_bucket_name)  # response =
        # print("@@@@@@@@@@@@@", response)
    except Exception as err:
        logger.exception(err)  # , exc_info=True
        raise err

    return {"storage": "healthy"}


def run_healthcheck() -> dict[str, str]:
    test_db()
    test_storage()
    return {"status": "ALIVE"}
