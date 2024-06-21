import boto3
from botocore.exceptions import ClientError

from .storage_interface import StorageInterface


class AWSS3Storage(StorageInterface):
    def __init__(self, bucket_name: str, aws_access_key_id: str, aws_secret_access_key: str, region_name: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def upload_file(self, file_path: str, destination_path: str) -> bool:
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, destination_path)
            return True
        except ClientError:
            return False

    def download_file(self, file_path: str, destination_path: str) -> bool:
        try:
            self.s3_client.download_file(self.bucket_name, file_path, destination_path)
            return True
        except ClientError:
            return False

    def delete_file(self, file_path: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError:
            return False

    def list_files(self, prefix: str = "") -> list:
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError:
            return []

    def get_url(self, file_path: str, expiration: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=expiration
            )
            return url
        except ClientError:
            return ""
