import io
from typing import Optional
from uuid import uuid4

# import magic
from fastapi import APIRouter, Depends, Request, UploadFile
from loguru import logger

# from sqlmodel import Session, select
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.config import get_settings
from app.db import get_session
from app.models.models import Files
from app.service.aws_s3 import s3_client, s3_resource

settings = get_settings()
s3_router = APIRouter()


@s3_router.post("/create_bucket")
def post_create_bucket():
    logger.info("👋 from S3 route")
    prefix = "mgu"
    bucket_name = "".join([prefix, "-", "dc5b9aefbee54953824d9fc327df7faf"])  # str(uuid.uuid4().hex)
    # mgu-dc5b9aefbee54953824d9fc327df7faf
    location = {"LocationConstraint": settings.s3_region}

    try:
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    except BaseException as error:
        print(error)

    return bucket_name


@s3_router.get("/list_buckets")
@logger.catch()
def get_buckets_list():
    s3_buckets = []
    response = s3_client.list_buckets()

    print("Listing Amazon S3 Buckets:")

    for bucket in response["Buckets"]:
        s3_buckets.append(bucket["Name"])
        print(f"-- {bucket['Name']}")
    return s3_buckets


@s3_router.get("/list_files")
@logger.catch()
def get_files_list(*, session: Session = Depends(get_session)):

    # https://realpython.com/python-boto3-aws-s3/#object-traversal
    # bucket = s3_resource.Bucket(name=settings.s3_bucket_name)

    files = []

    # for obj in bucket.objects.all():
    #     files.append({"name": obj.key})
    #     print(obj.key)
    # subsrc = obj.Object()
    # print(obj.key, obj.storage_class, obj.last_modified, subsrc.version_id, subsrc.metadata)

    return files


# @s3_router.delete("/dlete_bucket/{bucket_name}")
# def remove_bucket(bucket_name: str):

#     for s3_object in s3_resource.Bucket(bucket_name).objects.all():
#         s3_object.delete()
#     # Deleting objects versions if S3 versioning enabled
#     for s3_object_ver in s3_resource.Bucket(bucket_name).object_versions.all():
#         s3_object_ver.delete()

#     response = s3_client.delete_bucket(Bucket=bucket_name)
#     return response


@s3_router.delete("/delete_file/")
def remove_bucket(*, session: Session = Depends(get_session), objectName: str):

    a = s3_resource.Object(settings.s3_bucket_name, objectName).delete()
    print(a)

    db_task = session.exec(select(Files).where(Files.file_name == objectName)).one_or_none()
    session.delete(db_task)
    session.commit()

    return {"msg": "ok"}


@s3_router.get("/get_s3_obj/")
def get_s3(s3_obj: str):
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

    # f.seek(0)
    # mime_type = magic.from_buffer(f.read(2048), mime=True)

    f.seek(0)
    header = {"Content-Disposition": f'inline; filename="{s3_obj}"'}
    return StreamingResponse(f, headers=header)  # media_type=mime_type,


@s3_router.post("/upload/")
@logger.catch()
def upload_aws_s3(*, session: Session = Depends(get_session), request: Request, file: Optional[UploadFile] = None):
    if not file:
        return {"message": "No file sent"}

    # https://www.youtube.com/watch?v=JKlOlDFwsao
    # https://github.com/search?q=upload_fileobj+fastapi&type=code

    # s3_resource.Bucket(settings.s3_bucket_name).upload_fileobj(
    #     Fileobj=file.file,
    #     Key=f"folder/{objectName}",
    # ExtraArgs={
    #     "ContentType": "image/png",
    #     "ACL": "public-read",
    # },
    # )

    quota = session.exec(select([func.sum(Files.size)]).where(Files.account_id == 2)).one()
    print("quota", quota)

    # if quota > 300000:
    #     raise HTTPException(status_code=413, detail="Quota exceeded")

    s3_resource.Bucket(settings.s3_bucket_name).upload_fileobj(Fileobj=file.file, Key=file.filename)

    new_file = Files(
        uuid=str(uuid4()),
        account_id=2,
        owner_id=2,
        file_name=file.filename,
        file_id=1,
        extension="jpg",
        mimetype=file.content_type,
        size=request.headers["content-length"],
    )

    session.add(new_file)
    session.commit()
    session.refresh(new_file)

    return {"mime": file.content_type, "filename": f"{file.filename}", "uuid": new_file.uuid}


@s3_router.get("/upload_signed_url")
def sign_s3_upload(objectName: str):

    try:
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": objectName},
            ExpiresIn=3600,
            HttpMethod="PUT",
        )
    except BaseException:
        return None

    return url


@s3_router.get("/download_signed_url")
def sign_s3_download(tenant: str, file: str) -> str:

    url = s3_client.generate_presigned_url(
        ClientMethod="get_object", Params={"Bucket": settings.s3_bucket_name, "Key": f"folder/{file}"}, ExpiresIn=3600
    )

    return url
