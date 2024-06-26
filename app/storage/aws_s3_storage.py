import io
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from app.utils.filename_utils import get_safe_filename

from .storage_interface import StorageInterface


class AWSS3Storage(StorageInterface):
    def __init__(self, bucket_name: str, aws_access_key_id: str, aws_secret_access_key: str, region_name: str):
        self.bucket_name = bucket_name
        self.s3_resource = boto3.resource(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.s3_client = self.s3_resource.meta.client

    def upload_file(self, file_obj: BinaryIO, destination_path: str) -> bool:
        try:
            # Ensure the filename is safe
            safe_filename = get_safe_filename(Path(destination_path).name)
            safe_destination_path = str(Path(destination_path).with_name(safe_filename))

            self.s3_client.upload_fileobj(file_obj, self.bucket_name, safe_destination_path)
            return True
        except ClientError:
            return False

    def delete_file(self, file_path: str) -> bool:
        try:
            self.s3_resource.Object(self.bucket_name, file_path).delete()
            return True
        except ClientError as e:
            # Check if the error is a 404 (Not Found) or other client errors
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                logger.error(f"File {file_path} not found in bucket {self.bucket_name}.")
            else:
                logger.error(f"Client error occurred: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            # Handle any other exceptions
            logger.error(f"An unexpected error occurred: {str(e)}")
            return False

    def get_url(self, file_path: str, expiration: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object", Params={"Bucket": self.bucket_name, "Key": file_path}, ExpiresIn=expiration
            )
            return url
        except ClientError:
            return ""

    def download_file(self, file_path: str) -> BinaryIO:
        try:
            file_obj = io.BytesIO()
            self.s3_resource.Bucket(self.bucket_name).download_fileobj(file_path, file_obj)
            file_obj.seek(0)
            return file_obj
        except ClientError as e:
            logger.error(f"Client error occurred: {e.response['Error']['Message']}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            raise

    def list_files(self, prefix: str = "") -> list: ...
