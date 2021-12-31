import io
import mimetypes

import boto3
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from app.config import get_settings

settings = get_settings()
s3_router = APIRouter()


s3 = boto3.resource(
    service_name="s3",
    region_name=settings.s3_region,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_access_key,
)


@s3_router.get("/get_bucket_names")
async def get_all_bucket_names():
    s3_buckets = []
    for bucket in s3.buckets.all():
        s3_buckets.append(bucket.name)
    return s3_buckets


@s3_router.post("/get_s3_obj/")
async def get_s3(s3_obj: str):
    """
    Retreives an s3 jpg image and streams it back.
    ### Request Body
    - `s3_obj`: str
        #### The S3 Object's string

    ### Response
    Streamed image
    """
    f = io.BytesIO()
    s3.Bucket(settings.s3_bucket_name).download_fileobj(s3_obj, f)
    f.seek(0)
    return StreamingResponse(
        f, media_type="image/jpg", headers={"Content-Disposition": 'inline; filename="%s.jpg"' % (object,)}
    )


@s3_router.post("/upload/")
async def upload_aws_s3(file: UploadFile = File(...)):

    # https://www.youtube.com/watch?v=JKlOlDFwsao
    # https://github.com/search?q=upload_fileobj+fastapi&type=code

    # bucket names
    for bucket in s3.buckets.all():
        print(bucket.name)

    s3.Bucket(settings.s3_bucket_name).upload_fileobj(
        Fileobj=file.file,
        Key="img.png",
        # ExtraArgs={
        #     "ContentType": "image/png",
        #     "ACL": "public-read",
        # },
    )

    # session = Session(aws_access_key_id=settings.s3_access_key, aws_secret_access_key=settings.s3_secret_access_key)
    # s3 = session.resource("s3")
    # your_bucket = s3.Bucket(settings.s3_bucket_name)

    # filename = file.filename
    # data = file.file._file

    # s3.Bucket(settings.s3_bucket_name).upload_file(key=filename, fileobject=data)

    # for s3_file in your_bucket.objects.all():
    #     print(s3_file.key)

    # s3 = S3Client(
    #     AsyncClient,
    #     S3Config(
    #         settings.s3_access_key, settings.s3_secret_access_key, settings.s3_region, settings.s3_bucket_name + ".com"
    #     ),
    # )
    # await s3.upload("path/to/upload-to.txt", b"this the content")

    # files = [f for f in s3.list()]

    # # print(settings.s3_region)
    # print(settings.s3_access_key, settings.s3_secret_access_key, settings.s3_region, settings.s3_bucket_name)
    return {"region": settings.s3_region, "files": "files", "filename": file.filename}
    # return {"filename": file.filename}


@s3_router.get("/sign")
def sign_s3_upload(objectName: str):
    boto3_session = boto3.Session(
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_access_key,
    )

    s3 = boto3_session.client("s3")
    mime_type, _ = mimetypes.guess_type(objectName)
    presigned_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.s3_bucket_name,
            "Key": objectName,
            "ContentType": mime_type,
            "ACL": "public-read",
        },
        ExpiresIn=3600,
    )

    return {"signedUrl": presigned_url}
