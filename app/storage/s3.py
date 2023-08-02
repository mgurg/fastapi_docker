import os
import re
from pathlib import Path
from typing import BinaryIO

from app.config import get_settings
from app.storage.base import BaseStorage

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None

settings = get_settings()


class S3Storage(BaseStorage):
    """
    Amazon S3 or any S3 compatible storage backend.
    You might want to use this with the `FileType` type.
    Requires `boto3` to be installed.
    """

    AWS_ACCESS_KEY_ID = settings.s3_access_key
    """AWS access key ID. Either set here or as an environment variable."""

    AWS_SECRET_ACCESS_KEY = settings.s3_secret_access_key
    """AWS secret access key. Either set here or as an environment variable."""

    AWS_S3_REGION = settings.s3_region
    """AWS S3 bucket name to use."""

    AWS_S3_BUCKET_NAME = settings.s3_bucket_name
    """AWS S3 bucket name to use."""

    AWS_S3_ENDPOINT_URL = ""
    """AWS S3 endpoint URL."""

    AWS_S3_USE_SSL = True
    """Indicate if SSL should be used."""

    AWS_DEFAULT_ACL = ""
    """Optional ACL set on the object like `public-read`.
    By default file will be private."""

    AWS_QUERYSTRING_AUTH = False
    """Indicate if query parameter authentication should be used in URLs."""

    AWS_S3_CUSTOM_DOMAIN = ""
    """Custom domain to use for serving object URLs."""

    def __init__(self) -> None:
        print("REGION", self.AWS_S3_REGION)
        assert boto3 is not None, "'boto3' is not installed"
        assert not self.AWS_S3_ENDPOINT_URL.startswith("http"), "URL should not contain protocol"

        self._http_scheme = "https" if self.AWS_S3_USE_SSL else "http"
        self._url = f"{self._http_scheme}://{self.AWS_S3_ENDPOINT_URL}"
        self._s3 = boto3.resource(
            "s3",
            region_name=self.AWS_S3_REGION,
            # endpoint_url=self._url,
            use_ssl=self.AWS_S3_USE_SSL,
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
        )
        self._bucket = self._s3.Bucket(name=self.AWS_S3_BUCKET_NAME)

    def secure_filename(self, filename: str) -> str:
        """
        From Werkzeug secure_filename.
        """
        _filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
        for sep in os.path.sep, os.path.altsep:
            if sep:
                filename = filename.replace(sep, " ")

        normalized_filename = _filename_ascii_strip_re.sub("", "_".join(filename.split()))
        filename = str(normalized_filename).strip("._")
        return filename

    def get_name(self, name: str) -> str:
        """
        Get the normalized name of the file.
        """

        filename = self.secure_filename(Path(name).name)
        return str(Path(name).with_name(filename))

    def get_size(self, name: str) -> int:
        """
        Get file size in bytes.
        """

        key = self.get_name(name)
        return self._bucket.Object(key).content_length

    def get_path(self, name: str) -> str:
        """
        Get full URL to the file.
        """

        key = self.get_name(name)

        if self.AWS_S3_CUSTOM_DOMAIN:
            return f"{self._http_scheme}://{self.AWS_S3_CUSTOM_DOMAIN}/{key}"

        if self.AWS_QUERYSTRING_AUTH:
            params = {"Bucket": self._bucket.name, "Key": key}
            return self._s3.meta.client.generate_presigned_url("get_object", Params=params)

        return f"{self._http_scheme}://{self.AWS_S3_ENDPOINT_URL}/{self.AWS_S3_BUCKET_NAME}/{key}"

    def write(self, file: BinaryIO, name: str) -> str:
        """
        Write input file which is opened in binary mode to destination.
        """

        file.seek(0, 0)
        key = self.get_name(name)

        self._bucket.upload_fileobj(Fileobj=file, Key=name)  # , ExtraArgs={"ACL": self.AWS_DEFAULT_ACL}
        return key

    def read(self):
        ...

    def remove_file(self):
        ...
