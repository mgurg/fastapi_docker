import io
import pathlib
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy import func
from sqlmodel import Session, select
from starlette.responses import StreamingResponse

from app.config import get_settings
from app.db import get_session

# from app.models.models import FileResponse, File, FileUrlResponse, StandardResponse
from app.model.model import File
from app.schema.schema import FileResponse, FileUrlResponse, StandardResponse
from app.service.aws_s3 import s3_client, s3_resource
from app.service.bearer_auth import has_token

settings = get_settings()

file_router = APIRouter()


@file_router.get("/index", response_model=List[FileResponse], name="user:Profile")
async def file_get_info_all(*, session: Session = Depends(get_session), auth=Depends(has_token)):

    # quota = session.execute(select([func.sum(File.size)]).where(File.account_id == 2)).one()
    # print("quota", quota)
    # if quota > 300000:
    #     raise HTTPException(status_code=413, detail="Quota exceeded")

    files = (
        session.execute(select(File).where(File.account_id == auth["account"]).where(File.deleted_at.is_(None)))
        .scalars()
        .all()
    )

    return files


@file_router.get("/{uuid}", response_model=FileUrlResponse, name="file:GetInfoFromDB")
async def file_get_info_single(*, session: Session = Depends(get_session), uuid: UUID, auth=Depends(has_token)):

    file = session.execute(
        select(File)
        .where(File.account_id == auth["account"])
        .where(File.uuid == uuid)
        .where(File.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # file = dict(file)
    # file["url"] = "https://placeimg.com/500/300/nature?t=" + file["file_name"]

    return file


@file_router.post("/", response_model=FileResponse, name="file:Upload")
async def file_add(
    *,
    session: Session = Depends(get_session),
    request: Request,
    file: Optional[UploadFile] = None,
    auth=Depends(has_token),
):

    if not file:
        raise HTTPException(status_code=400, detail="No file sent")

    quota = session.execute(select([func.sum(File.size)]).where(File.account_id == 2)).one()
    print("quota", quota)
    # if quota > 500000:
    #     raise HTTPException(status_code=413, detail="Quota exceeded")

    s3_folder_path = str(auth["account"]) + "/" + file.filename
    s3_flat_path = file.filename

    s3_resource.Bucket(settings.s3_bucket_name).upload_fileobj(Fileobj=file.file, Key=s3_folder_path)

    new_file = File(
        uuid=str(uuid4()),
        account_id=auth["account"],
        owner_id=auth["user"],
        file_name=file.filename,
        file_id=1,
        extension=pathlib.Path(file.filename).suffix,
        mimetype=file.content_type,
        size=request.headers["content-length"],
        created_at=datetime.utcnow(),
    )

    session.add(new_file)
    session.commit()
    session.refresh(new_file)

    # return {"mime": file.content_type, "filename": f"{file.filename}", "uuid": new_file.uuid}

    return new_file


@file_router.delete("/{uuid}", response_model=StandardResponse)
async def remove_bucket(*, session: Session = Depends(get_session), uuid: UUID, auth=Depends(has_token)):

    db_file = session.execute(
        select(File).where(File.account_id == 2).where(File.uuid == uuid).where(File.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not db_file:
        raise HTTPException(status_code=400, detail="File not found")

    s3_folder_path = str(db_file.account_id) + "/" + db_file.file_name
    s3_flat_path = db_file.file_name

    s3_resource.Object(settings.s3_bucket_name, s3_folder_path).delete()

    session.delete(db_file)
    session.commit()

    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/
    # TODO: delete every day empty files
    return {"ok": True}


@file_router.get("/download/{uuid}", name="file:Download")
async def file_download(*, session: Session = Depends(get_session), uuid: UUID):

    db_file = session.execute(
        select(File)
        # .where(File.account_id == auth["account"])
        .where(File.uuid == uuid).where(File.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    s3_folder_path = str(db_file.account_id) + "/" + db_file.file_name
    s3_flat_path = db_file.file_name

    f = io.BytesIO()
    s3_resource.Bucket(settings.s3_bucket_name).download_fileobj(s3_folder_path, f)

    f.seek(0)
    header = {"Content-Disposition": f'inline; filename="{db_file.file_name}"'}
    return StreamingResponse(f, media_type=db_file.mimetype, headers=header)
