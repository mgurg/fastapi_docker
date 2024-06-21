from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

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
        except ClientError:
            return False

    def get_url(self, file_path: str, expiration: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object", Params={"Bucket": self.bucket_name, "Key": file_path}, ExpiresIn=expiration
            )
            return url
        except ClientError:
            return ""

    def download_file(self, file_path: str, destination_path: str) -> bool: ...

    def list_files(self, prefix: str = "") -> list: ...
