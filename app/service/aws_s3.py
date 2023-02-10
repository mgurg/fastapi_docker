import boto3

from app.config import get_settings

settings = get_settings()

s3_resource = boto3.resource(
    service_name="s3",
    region_name=settings.s3_region,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_access_key,
)

s3_client = boto3.client(
    "s3",
    region_name=settings.s3_region,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_access_key,
)


def generate_presigned_url(tenant: str, file: str) -> str:
    presigned_url = s3_client.generate_presigned_url(
        ClientMethod="get_object", Params={"Bucket": settings.s3_bucket_name, "Key": f"{tenant}/{file}"}, ExpiresIn=3600
    )
    return presigned_url
