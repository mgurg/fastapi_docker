from datetime import datetime, time, timedelta
from typing import List

import pendulum
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from loguru import logger
from passlib.hash import argon2
from sqlalchemy import func, true
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import (
    Events,
    StandardResponse,
    TaskAddIn,
    TaskEditIn,
    TaskIndexResponse,
    Tasks,
    TaskSingleResponse,
    Users,
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
    tasks = session.exec(select(Tasks).where(Tasks.deleted_at == None).offset(offset).limit(limit)).all()

    return tasks


@task_router.get("/{uuid}", response_model=TaskSingleResponse, name="Get task")
async def user_get_all(*, session: Session = Depends(get_session), uuid):
    task = session.exec(select(Tasks).where(Tasks.uuid == uuid).where(Tasks.deleted_at == None)).one_or_none()
    return task


@task_router.post("/add", response_model=StandardResponse, name="task:Tasks")
@logger.catch()
async def user_get_all(*, session: Session = Depends(get_session), task: TaskAddIn):

    res = TaskAddIn.from_orm(task)

    assignee = None
    if res.assignee is not None:
        db_assignee = session.exec(
            select(Users).where(Users.uuid == res.assignee).where(Users.deleted_at == None)
        ).one_or_none()
        if not db_assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
        assignee = db_assignee.id

    events = []
    req_fields = [res.at_Mo, res.at_Tu, res.at_We, res.at_Th, res.at_Fr, res.at_Sa, res.at_Su, res.freq]

    if (all(v is not None for v in req_fields)) & (res.recurring == True):
        new_event = Events(
            uuid=get_uuid(),
            client_id=2,
            recurring=True,
            interval=1,
            freq=res.freq,
            at_mo=res.at_Mo,
            at_tu=res.at_Tu,
            at_we=res.at_We,
            at_th=res.at_Th,
            at_fr=res.at_Fr,
            at_sa=res.at_Sa,
            at_su=res.at_Su,
            date_from=datetime.utcnow(),
            date_to=datetime.utcnow() + timedelta(days=3),
            occurrence_number=10,
            all_day=res.all_day,
        )
        events = [new_event]

    time_from = None
    time_to = None

    if res.date_from is not None:
        time_from = pendulum.instance(res.date_from).format("HH:mm:ssZ")
    if res.date_to is not None:
        time_to = pendulum.instance(res.date_to).format("HH:mm:ssZ")

    new_task = Tasks(
        uuid=get_uuid(),
        client_id=2,
        author_id=1,
        assignee_id=assignee,
        title=res.title,
        description=res.description,
        color=res.color,
        date_from=res.date_from,
        date_to=res.date_to,
        time_from=time_from,
        time_to=time_to,
        priority=res.priority,
        duration=0,
        is_active=True,
        all_day=res.all_day,
        recurring=res.recurring,
        type=res.type,
        created_at=datetime.utcnow(),
        events=events,
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return {"ok": True}


@task_router.patch("/{uuid}", response_model=StandardResponse, name="task:Tasks")
@logger.catch()
async def user_get_all(*, session: Session = Depends(get_session), uuid, task: TaskEditIn):

    db_task = session.exec(select(Tasks).where(Tasks.uuid == uuid).where(Tasks.deleted_at == None)).one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task.dict(exclude_unset=True)
    if task_data["assignee"] is not None:
        db_assignee = session.exec(
            select(Users).where(Users.uuid == task_data["assignee"]).where(Users.deleted_at == None)
        ).one_or_none()
        if not db_assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")

        task_data["assignee_id"] = db_assignee.id
        del task_data["assignee"]

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

    # db_task.events.remove()

    # TODO: Delete Events
    for event in db_task.events:
        db_event = session.exec(select(Events).where(Events.id == event.id)).one()
        db_task.events.remove(event)
        session.delete(db_event)
        session.commit()

    session.delete(db_task)
    session.commit()

    # update_package = {"deleted_at": datetime.utcnow()}  # soft delete
    # for key, value in update_package.items():
    #     setattr(db_task, key, value)

    # session.add(db_task)
    # session.commit()
    # session.refresh(db_task)

    return {"ok": True}
