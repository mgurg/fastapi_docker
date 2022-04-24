import io
import pathlib
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.security import HTTPBearer
from sqlalchemy import func
from sqlmodel import Session, select
from starlette.responses import StreamingResponse

from app.config import get_settings
from app.db import get_session
from app.models.models import FileResponse, Files, FileUrlResponse, StandardResponse
from app.service.aws_s3 import s3_client, s3_resource
from app.service.bearer_auth import has_token
from app.service.helpers import get_uuid

settings = get_settings()

file_router = APIRouter()


@file_router.get("/index", response_model=List[FileResponse], name="user:Profile")
async def file_get_all(*, session: Session = Depends(get_session), auth=Depends(has_token)):

    # quota = session.exec(select([func.sum(Files.size)]).where(Files.account_id == 2)).one()
    # print("quota", quota)
    # if quota > 300000:
    #     raise HTTPException(status_code=413, detail="Quota exceeded")

    files = session.exec(
        select(Files).where(Files.account_id == auth["account"]).where(Files.deleted_at.is_(None))
    ).all()

    return files


@file_router.get("/{uuid}", response_model=FileUrlResponse, name="user:Profile")
async def file_get_all(*, session: Session = Depends(get_session), uuid: UUID, auth=Depends(has_token)):

    file = session.exec(
        select(Files)
        .where(Files.account_id == auth["account"])
        .where(Files.uuid == uuid)
        .where(Files.deleted_at.is_(None))
    ).one_or_none()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # file = dict(file)
    # file["url"] = "https://placeimg.com/500/300/nature?t=" + file["file_name"]

    return file


@file_router.post("/", response_model=FileResponse, name="user:Profile")
async def file_add(
    *,
    session: Session = Depends(get_session),
    request: Request,
    file: Optional[UploadFile] = None,
    auth=Depends(has_token),
):

    if not file:
        raise HTTPException(status_code=400, detail="No file sent")

    quota = session.exec(select([func.sum(Files.size)]).where(Files.account_id == 2)).one()
    print("quota", quota)
    # if quota > 500000:
    #     raise HTTPException(status_code=413, detail="Quota exceeded")

    s3_resource.Bucket(settings.s3_bucket_name).upload_fileobj(Fileobj=file.file, Key=file.filename)

    new_file = Files(
        uuid=get_uuid(),
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

    db_file = session.exec(
        select(Files).where(Files.account_id == 2).where(Files.uuid == uuid).where(Files.deleted_at.is_(None))
    ).one_or_none()

    if not db_file:
        raise HTTPException(status_code=400, detail="File not found")

    s3_resource.Object(settings.s3_bucket_name, db_file.file_name).delete()

    session.delete(db_file)
    session.commit()

    # https://fastapi-utils.davidmontague.xyz/user-guide/repeated-tasks/
    # TODO: delete every day empty files
    return {"ok": True}


@file_router.get("/download/{uuid}", name="file:Download")
async def file_download(*, session: Session = Depends(get_session), uuid: UUID):

    file = session.exec(
        select(Files)
        # .where(Files.account_id == auth["account"])
        .where(Files.uuid == uuid).where(Files.deleted_at.is_(None))
    ).one_or_none()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    f = io.BytesIO()
    s3_resource.Bucket(settings.s3_bucket_name).download_fileobj(file.file_name, f)

    f.seek(0)
    header = {"Content-Disposition": f'inline; filename="{file.file_name}"'}
    return StreamingResponse(f, media_type=file.mimetype, headers=header)
