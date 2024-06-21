from typing import Literal

from .aws_s3_storage import AWSS3Storage
from .storage_interface import StorageInterface


class StorageFactory:
    @staticmethod
    def get_storage_provider(provider: Literal["aws_s3"], **kwargs) -> StorageInterface:
        if provider.lower() == "aws_s3":
            return AWSS3Storage(
                bucket_name=kwargs.get("bucket_name"),
                aws_access_key_id=kwargs.get("aws_access_key_id"),
                aws_secret_access_key=kwargs.get("aws_secret_access_key"),
                region_name=kwargs.get("region_name"),
            )
        else:
            raise ValueError(f"Unsupported storage provider: {provider}")
