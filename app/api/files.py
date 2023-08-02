import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.config import get_settings
from app.crud import crud_files
from app.db import get_db
from app.models.models import User
from app.schemas.responses import FileResponse, StandardResponse
from app.service.bearer_auth import has_token

# from app.models.models import FileResponse, Files, FileUrlResponse, StandardResponse
from app.storage.aws_s3 import generate_presigned_url, s3_resource

settings = get_settings()

file_router = APIRouter()

CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[Session, Depends(get_db)]
# UserDB = Annotated[Session, Depends(get_db)]


@file_router.get("/used_space")
def file_get_used_space(*, db: UserDB, auth_user: CurrentUser):
    db_file_size = crud_files.get_files_size_in_db(db)

    return db_file_size


@file_router.get("/", response_model=list[FileResponse])
def file_get_info_all(*, db: UserDB, auth_user: CurrentUser):
    if db is None:
        raise HTTPException(status_code=500, detail="General Error")

    # quota = session.exec(select([func.sum(Files.size)]).where(Files.account_id == 2)).one()
    # print("quota", quota)
    # if quota > 300000:
    #     raise HTTPException(status_code=413, detail="Quota exceeded")

    # files = session.exec(
    #     select(Files).where(Files.account_id == auth["account"]).where(Files.deleted_at.is_(None))
    # ).all()

    db_files = crud_files.get_files(db)

    return db_files
    # pass


@file_router.get("/{uuid}", response_model=FileResponse, name="file:GetInfoFromDB")
def file_get_info_single(*, db: UserDB, uuid: UUID, auth_user: CurrentUser):
    db_file = crud_files.get_file_by_uuid(db, uuid)

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # file = dict(file)
    # file["url"] = "https://placeimg.com/500/300/nature?t=" + file["file_name"]

    return db_file


@file_router.post("/", response_model=FileResponse)
def file_add(
    *,
    db: UserDB,
    request: Request,
    auth_user: CurrentUser,
    file: UploadFile | None = None,
    uuid: UUID | None = Form(None),
):
    if not file:
        raise HTTPException(status_code=400, detail="No file sent")

    quota = crud_files.get_files_size_in_db(db)
    if quota > 50000000:  # ~5MB
        raise HTTPException(status_code=413, detail="Quota exceeded")

    if not uuid:
        file_uuid = str(uuid4())
    else:
        file_uuid = uuid

    try:
        s3_folder_path = "".join([str(request.headers.get("tenant", "None")), "/", file_uuid, "_", file.filename])
        # print(s3_folder_path)

        s3_resource.Bucket(settings.s3_bucket_name).upload_fileobj(Fileobj=file.file, Key=s3_folder_path)
    except Exception as e:
        print(e)

    file_data = {
        "uuid": file_uuid,
        "owner_id": auth_user.id,
        "file_name": file.filename,
        "file_description": None,
        "extension": Path(file.filename).suffix,
        "mimetype": file.content_type,
        "size": request.headers["content-length"],
        "created_at": datetime.now(timezone.utc),
    }

    new_file = crud_files.create_file(db, file_data)

    new_file.url = generate_presigned_url(
        request.headers.get("tenant", "public"), "_".join([str(file_uuid), file.filename])
    )

    # file.close()
    return new_file


@file_router.delete("/{file_uuid}", response_model=StandardResponse)
def remove_bucket(*, db: UserDB, request: Request, file_uuid: UUID, auth_user: CurrentUser):
    db_file = crud_files.get_file_by_uuid(db, file_uuid)

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    s3_folder_path = "".join([str(request.headers.get("tenant", "None")), "/", str(file_uuid), "_", db_file.file_name])

    try:
        s3_resource.Object(settings.s3_bucket_name, s3_folder_path).delete()
    except Exception as e:
        capture_exception(e)
        print(e)

    db.delete(db_file)
    db.commit()

    return {"ok": True}


@file_router.get("/download/{file_uuid}", name="file:Download")
def file_download(*, db: UserDB, request: Request, file_uuid: UUID):
    db_file = crud_files.get_file_by_uuid(db, file_uuid)

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        s3_folder_path = "".join([str(request.headers.get("tenant")), "/", str(file_uuid), "_", db_file.file_name])
        print(s3_folder_path)

        f = io.BytesIO()
        s3_resource.Bucket(settings.s3_bucket_name).download_fileobj(s3_folder_path, f)

        f.seek(0)
        header = {"Content-Disposition": f'inline; filename="{db_file.file_name}"'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(f, media_type=db_file.mimetype, headers=header)


@file_router.get("/download/", name="file:Download")
def file_download_pre_signed(tenant, file):
    url = generate_presigned_url(tenant, file)
    return url


@file_router.get("/video_upload_token/", name="video:token")
def video_upload_token(auth_user: CurrentUser):
    # #  https://api.video/blog/tutorials/delegated-uploads
    # # Part One
    # payload = json.dumps({"apiKey": "47yczv1m0huXDEg6iyNRqYT9QXmUcMAArHY0Qqzgz0I"})
    # headers = {"accept": "application/json", "content-type": "application/json"}

    # response = requests.post("https://sandbox.api.video/auth/api-key", headers=headers, data=payload)

    # print(response.text)  # get Bearer Token

    # #  Part Two

    # payload = {}
    # headers = {
    #     "accept": "application/vnd.api.video+json",
    #     "Authorization": "Bearer 5dZBuv0dF7w0SG6V1Py1Ho5eqNT_Jk3zpRUeeIj3tPHzswdGEBRPcT9Ytw",
    # }

    # response = requests.post("https://sandbox.api.video/upload-tokens", headers=headers, data=payload)

    # print(response.text)  # final upload token

    # url = generate_presigned_url(tenant, file)

    upload_token = settings.API_VIDEO_UPLOAD
    api_token = settings.API_VIDEO
    return {"api_token": api_token, "upload_token": upload_token}
