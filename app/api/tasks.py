from datetime import datetime, time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import (
    StandardResponse,
    TaskAddIn,
    TaskEditIn,
    TaskIndexResponse,
    Tasks,
)
from app.service.helpers import get_uuid
from app.service.password import Password

task_router = APIRouter()


@task_router.get("/index", response_model=List[TaskIndexResponse], name="List tasks")
async def user_get_all(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=20, lte=100),
):
    users = session.exec(select(Tasks).where(Tasks.deleted_at == None).offset(offset).limit(limit)).all()
    return users


@task_router.get("/{uuid}", response_model=TaskIndexResponse, name="List tasks")
async def user_get_all(*, session: Session = Depends(get_session), uuid):
    users = session.exec(select(Tasks).where(Tasks.uuid == uuid).where(Tasks.deleted_at == None)).first()
    return users


@task_router.post("/add", response_model=StandardResponse, name="task:Tasks")
async def user_get_all(*, session: Session = Depends(get_session), task: TaskAddIn):

    res = TaskAddIn.from_orm(task)

    new_task = Tasks(
        uuid=get_uuid(),
        client_id=2,
        author_id=1,
        assignee_id=1,
        title=res.title,
        description=res.description,
        date_from=res.date_from,
        date_to=res.date_to,
        priority=res.priority,
        duration=0,
        is_active=True,
        type=res.type,
        connected_tasks=res.connected_tasks,
        created_at=datetime.utcnow(),
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return {"ok": True}


@task_router.patch("/{uuid}", response_model=StandardResponse, name="task:Tasks")
async def user_get_all(*, session: Session = Depends(get_session), uuid, task: TaskEditIn):

    db_task = session.exec(select(Tasks).where(Tasks.uuid == uuid).where(Tasks.deleted_at == None)).one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task.dict(exclude_unset=True)

    for key, value in task_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return {"ok": True}


@task_router.delete("/{uuid}", response_model=StandardResponse, name="task:Tasks")
async def user_get_all(*, session: Session = Depends(get_session), uuid):

    db_task = session.exec(select(Tasks).where(Tasks.uuid == uuid).where(Tasks.deleted_at == None)).one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_package = {"deleted_at": datetime.utcnow()}  # soft delete
    for key, value in update_package.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return {"ok": True}
