import io
import logging
import mimetypes
import uuid

import boto3
from fastapi import APIRouter, File, UploadFile
from loguru import logger
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from app.config import get_settings

settings = get_settings()
s3_router = APIRouter()


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


@s3_router.post("/create_bucket")
async def post_create_bucket():
    logger.info("👋 from S3 route")
    prefix = "mgu"
    bucket_name = prefix + "-" + "dc5b9aefbee54953824d9fc327df7faf"  # str(uuid.uuid4().hex)
    # mgu-dc5b9aefbee54953824d9fc327df7faf
    location = {"LocationConstraint": settings.s3_region}

    try:
        response = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    except BaseException as error:
        print(error)

    return bucket_name


@s3_router.get("/list_buckets")
@logger.catch()
async def get_buckets_list():
    s3_buckets = []
    response = s3_client.list_buckets()

    print("Listing Amazon S3 Buckets:")

    for bucket in response["Buckets"]:
        s3_buckets.append(bucket["Name"])
        print(f"-- {bucket['Name']}")
    return s3_buckets


@s3_router.delete("/bucket/{bucket_name}")
async def remove_bucket(bucket_name: str):

    for s3_object in s3_resource.Bucket(bucket_name).objects.all():
        s3_object.delete()
    # Deleting objects versions if S3 versioning enabled
    for s3_object_ver in s3_resource.Bucket(bucket_name).object_versions.all():
        s3_object_ver.delete()

    response = s3_client.delete_bucket(Bucket=bucket_name)
    return response


@s3_router.get("/get_s3_obj/")
async def get_s3(s3_obj: str, bucket_name: str):
    """
    Retreives an s3 jpg image and streams it back.
    ### Request Body
    - `s3_obj`: str
        #### The S3 Object's string

    ### Response
    Streamed image
    """
    f = io.BytesIO()
    s3_resource.Bucket(settings.s3_bucket_name).download_fileobj(s3_obj, f)
    f.seek(0)
    return StreamingResponse(
        f, media_type="image/jpg", headers={"Content-Disposition": f'inline; filename="{s3_obj}"'}
    )


@s3_router.post("/upload/{objectName}")
@logger.catch()
async def upload_aws_s3(objectName: str, file: UploadFile = File(...)):

    # https://www.youtube.com/watch?v=JKlOlDFwsao
    # https://github.com/search?q=upload_fileobj+fastapi&type=code

    s3_resource.Bucket(settings.s3_bucket_name).upload_fileobj(
        Fileobj=file.file,
        Key=f"folder/{objectName}",
        # ExtraArgs={
        #     "ContentType": "image/png",
        #     "ACL": "public-read",
        # },
    )

    return {"region": settings.s3_region, "files": "files", "filename": f"folder/{file.filename}"}


@s3_router.get("/upload_signed_url")
def sign_s3_upload(objectName: str):

    try:
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": objectName},
            ExpiresIn=3600,
            HttpMethod="PUT",
        )
    except BaseException as error:
        return None

    return url


@s3_router.get("/download_signed_url")
def sign_s3_download(file: str):

    url = s3_client.generate_presigned_url(
        ClientMethod="get_object", Params={"Bucket": settings.s3_bucket_name, "Key": f"folder/{file}"}, ExpiresIn=3600
    )

    return url
