from functools import lru_cache

from app.config import get_settings
from app.storage.storage_factory import StorageFactory

settings = get_settings()


@lru_cache()
def get_storage_provider():
    return StorageFactory.get_storage_provider(
        "aws_s3",
        bucket_name=settings.AWS_BUCKET_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME
    )
