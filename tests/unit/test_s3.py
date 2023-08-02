import os
from pathlib import Path

import boto3
from moto import mock_s3

from app.storage.s3 import S3Storage

os.environ["MOTO_S3_CUSTOM_ENDPOINTS"] = "http://custom.s3.endpoint"


class PrivateS3Storage(S3Storage):
    AWS_ACCESS_KEY_ID = "access"
    AWS_SECRET_ACCESS_KEY = "secret"
    AWS_S3_BUCKET_NAME = "bucket"
    AWS_S3_ENDPOINT_URL = "custom.s3.endpoint"
    AWS_S3_USE_SSL = False


@mock_s3
def test_s3_storage_methods(tmp_path: Path) -> None:
    # s3 = boto3.client("s3")
    # s3.create_bucket(Bucket="bucket")

    # tmp_file = tmp_path / "example.txt"
    # tmp_file.write_bytes(b"123")

    storage = PrivateS3Storage()

    assert storage.get_name("test (1).txt") == "test_1.txt"