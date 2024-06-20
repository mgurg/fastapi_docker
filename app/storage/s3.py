import os
import re
import unicodedata
from pathlib import Path
from typing import BinaryIO
from app.config import get_settings
from app.storage.base import BaseStorage
from app.storage.aws_s3 import s3_resource, generate_presigned_url

settings = get_settings()


class S3Storage(BaseStorage):
    """Amazon S3 storage backend."""

    def __init__(self):
        self.bucket = s3_resource.Bucket(settings.s3_bucket_name)

    def secure_filename(self, filename: str) -> str:
        """Sanitize the filename to be safe for storage."""
        filename = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")
        filename = re.sub(r"[^A-Za-z0-9_.-]", "", "_".join(filename.split()))
        filename = filename.strip("._")

        if os.name == "nt" and filename.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL",
                                                                  *(f"COM{i}" for i in range(10)),
                                                                  *(f"LPT{i}" for i in range(10))}:
            filename = f"_{filename}"

        return filename

    def get_name(self, name: str) -> str:
        """Get the normalized name of the file."""
        return self.secure_filename(Path(name).name)

    def get_size(self, name: str) -> int:
        """Get file size in bytes."""
        key = self.get_name(name)
        return self.bucket.Object(key).content_length

    def write(self, file: BinaryIO, name: str) -> str:
        """Write input file to S3."""
        file.seek(0)
        key = self.get_name(name)
        self.bucket.upload_fileobj(Fileobj=file, Key=key)
        return key

    def get_url(self, name: str) -> str:
        """Generate a presigned URL for the file."""
        key = self.get_name(name)
        return generate_presigned_url(settings.s3_bucket_name, key)
