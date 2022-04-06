from datetime import datetime, time, timedelta
from typing import List
from uuid import UUID

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
    Files,
    StandardResponse,
    TaskAddIn,
    TaskEditIn,
    TaskIndexResponse,
    Tasks,
    TaskSingleResponse,
    TasksLog,
    TasksLogIn,
    Users,
)
from app.service.bearer_auth import has_token
from app.service.helpers import get_uuid
from app.service.password import Password

task_router = APIRouter()


@task_router.get("/index", response_model=List[TaskIndexResponse], name="List tasks")
async def user_get_all(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=20, lte=100),
    auth=Depends(has_token)
):
    tasks = session.exec(
        select(Tasks)
        .where(Tasks.client_id == auth["account"])
        .where(Tasks.deleted_at.is_(None))
        .offset(offset)
        .limit(limit)
    ).all()

    return tasks


@task_router.get("/{task_uuid}", response_model=TaskSingleResponse, name="Get task")
async def user_get_all(*, session: Session = Depends(get_session), task_uuid: UUID, auth=Depends(has_token)):
    print(auth)
    task = session.exec(
        select(Tasks)
        .where(Tasks.client_id == auth["account"])
        .where(Tasks.uuid == task_uuid)
        .where(Tasks.deleted_at.is_(None))
    ).one_or_none()
    return task


@task_router.post("/add", response_model=StandardResponse, name="task:Tasks")
@logger.catch()
async def user_get_all(*, session: Session = Depends(get_session), task: TaskAddIn):

    res = TaskAddIn.from_orm(task)

    assignee = None
    if res.assignee is not None:
        db_assignee = session.exec(
            select(Users).where(Users.uuid == res.assignee).where(Users.deleted_at.is_(None))
        ).one_or_none()
        if not db_assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
        assignee = db_assignee.id

    files = []
    if res.files is not None:
        for file in res.files:
            db_file = session.exec(
                select(Files).where(Files.uuid == file).where(Files.deleted_at.is_(None))
            ).one_or_none()
            if db_file:
                files.append(db_file)

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
        mode=res.mode,
        created_at=datetime.utcnow(),
        events=events,
        file=files,
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return {"ok": True}


@task_router.patch("/{task_uuid}", response_model=StandardResponse, name="task:Tasks")
@logger.catch()
async def user_get_all(*, session: Session = Depends(get_session), task_uuid: UUID, task: TaskEditIn):

    db_task = session.exec(
        select(Tasks).where(Tasks.uuid == task_uuid).where(Tasks.deleted_at.is_(None))
    ).one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task.dict(exclude_unset=True)

    files = []
    if ("files" in task_data) and (task_data["files"] is not None):
        for file in db_task.file:
            db_task.file.remove(file)
        for file in task_data["files"]:
            db_file = session.exec(
                select(Files).where(Files.uuid == file).where(Files.deleted_at.is_(None))
            ).one_or_none()
            if db_file:
                files.append(db_file)

        task_data["file"] = files
        del task_data["files"]

    if ("assignee" in task_data) and (task_data["assignee"] is not None):
        db_assignee = session.exec(
            select(Users).where(Users.uuid == task_data["assignee"]).where(Users.deleted_at.is_(None))
        ).one_or_none()
        if not db_assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")

        task_data["assignee_id"] = db_assignee.id
        del task_data["assignee"]

    events = []
    if ("mode" in task_data) and (task_data["mode"] == "cyclic"):
        if db_task.events is not None:
            for event in db_task.events:
                db_event = session.exec(select(Events).where(Events.id == event.id)).one()
                db_task.events.remove(event)
                session.delete(db_event)
                session.commit()

        new_event = Events(
            uuid=get_uuid(),
            client_id=2,
            recurring=task_data["recurring"],
            interval=task_data["interval"],
            freq=task_data["freq"],
            at_mo=task_data["at_Mo"],
            at_tu=task_data["at_Tu"],
            at_we=task_data["at_We"],
            at_th=task_data["at_Th"],
            at_fr=task_data["at_Fr"],
            at_sa=task_data["at_Sa"],
            at_su=task_data["at_Su"],
            date_from=datetime.utcnow(),
            date_to=datetime.utcnow() + timedelta(days=3),
            occurrence_number=10,
            all_day=False,
        )
        task_data["events"] = [new_event]

        del task_data["recurring"]
        del task_data["interval"]
        del task_data["freq"]
        del task_data["at_Mo"]
        del task_data["at_Tu"]
        del task_data["at_We"]
        del task_data["at_Th"]
        del task_data["at_Fr"]
        del task_data["at_Sa"]
        del task_data["at_Su"]

    for key, value in task_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return {"ok": True}


@task_router.delete("/{task_uuid}", response_model=StandardResponse, name="task:Tasks")
async def user_get_all(*, session: Session = Depends(get_session), task_uuid: UUID):

    db_task = session.exec(
        select(Tasks).where(Tasks.uuid == task_uuid).where(Tasks.deleted_at.is_(None))
    ).one_or_none()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # db_task.events.remove()

    # TODO: Delete Events
    for event in db_task.events:
        db_event = session.exec(select(Events).where(Events.id == event.id)).one()
        db_task.events.remove(event)
        session.delete(db_event)
        session.commit()

    # Delete Files
    for file in db_task.file:
        db_file = session.exec(select(Files).where(Files.id == file.id)).one()
        db_task.file.remove(file)
        session.delete(db_file)
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


@task_router.post("/action/{task_uuid}", response_model=StandardResponse, name="task:Action")
@logger.catch()
async def task_action(*, session: Session = Depends(get_session), task_uuid: UUID, task: TasksLogIn):
    db_task = session.exec(select(Tasks).where(Tasks.uuid == task_uuid).where(Tasks.deleted_at.is_(None))).one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    res = TasksLogIn.from_orm(task)

    db_task_open_log = session.exec(
        select(TasksLog)
        .where(TasksLog.task_id == db_task.id)
        .where(TasksLog.action_type == "task")
        .order_by(TasksLog.id.desc())
    ).first()

    if (not db_task_open_log) and (res.action_type == "accepted" or res.action_type == "rejected"):
        first_task_log = TasksLog(
            task_id=db_task.id,
            uuid=get_uuid(),
            user_id=1,
            start_at=db_task.created_at,
            end_at=datetime.utcnow(),
            from_value="new",
            to_value=res.action_type,
            duration=pendulum.now().diff(pendulum.instance(db_task.created_at)).in_minutes(),
            action_type="task",
        )

        session.add(first_task_log)
        session.commit()
        session.refresh(first_task_log)

        db_task.status = res.action_type
        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        # ---------------------------------------

    if (db_task_open_log) and (db_task_open_log.to_value == "accepted" or db_task_open_log.to_value == "pause"):
        first_task_log = TasksLog(
            task_id=db_task.id,
            uuid=get_uuid(),
            user_id=1,
            start_at=datetime.utcnow(),
            from_value="start",
            duration=0,
            action_type="task",
        )

        session.add(first_task_log)
        session.commit()
        session.refresh(first_task_log)

        db_task.status = "in_progress"
        session.add(db_task)
        session.commit()
        session.refresh(db_task)

    if (db_task_open_log) and (db_task_open_log.end_at == None):
        if (db_task_open_log.from_value == "start") and (res.action_type == "stop"):
            duration = pendulum.now().diff(pendulum.instance(db_task_open_log.start_at)).in_minutes()

            db_task_open_log.end_at = datetime.utcnow()
            db_task_open_log.duration = duration
            db_task_open_log.to_value = res.action_type
            session.add(db_task_open_log)
            session.commit()
            session.refresh(db_task_open_log)

            db_task.status = "done"
            db_task.duration += duration
            session.add(db_task)
            session.commit()
            session.refresh(db_task)

        if (db_task_open_log.from_value == "start") and (res.action_type == "pause"):
            duration = pendulum.now().diff(pendulum.instance(db_task_open_log.start_at)).in_minutes()

            db_task_open_log.end_at = datetime.utcnow()
            db_task_open_log.duration = duration
            db_task_open_log.to_value = res.action_type
            session.add(db_task_open_log)
            session.commit()
            session.refresh(db_task_open_log)

            db_task.status = "paused"
            db_task.duration += duration
            session.add(db_task)
            session.commit()
            session.refresh(db_task)

        # if (db_task_open_log.from_value == "pause") and (res.action_type == "start"):
        #     duration = pendulum.now().diff(pendulum.instance(db_task_open_log.start_at)).in_minutes()

        #     db_task_open_log.end_at = datetime.utcnow()
        #     db_task_open_log.duration = duration
        #     db_task_open_log.to_value = res.action_type
        #     session.add(db_task_open_log)
        #     session.commit()
        #     session.refresh(db_task_open_log)

        #     db_task.status = "in_progress"
        #     db_task.duration += duration
        #     session.add(db_task)
        #     session.commit()
        #     session.refresh(db_task)

        # if (db_task_open_log.from_value == "pause") and (res.action_type == "stop"):
        #     duration = pendulum.now().diff(pendulum.instance(db_task_open_log.start_at)).in_minutes()

        #     db_task_open_log.end_at = datetime.utcnow()
        #     db_task_open_log.duration = duration
        #     db_task_open_log.to_value = res.action_type
        #     session.add(db_task_open_log)
        #     session.commit()
        #     session.refresh(db_task_open_log)

        #     db_task.status = "done"
        #     db_task.duration += duration
        #     session.add(db_task)
        #     session.commit()
        #     session.refresh(db_task)

    return {"ok": True}
