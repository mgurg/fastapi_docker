import itertools
import json
import operator
import pprint
from datetime import datetime
from typing import List
from uuid import uuid4

import pendulum
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY, rrule, rrulestr
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.hash import argon2
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import Events, TaskIndexResponse, Tasks
from app.validation.validation import Validation

event_router = APIRouter()


@event_router.get("/list", name="event:Index")
async def file_get_all(*, session: Session = Depends(get_session)):

    start = datetime.strptime("2022-03-01", "%Y-%m-%d")
    end = datetime.strptime("2022-03-28", "%Y-%m-%d")

    events_dict = [
        {
            "uuid": "38ec4397-643e-42be-b937-169f443a81a1",
            "title": "Task #1",
            "desc": "Desc #1",
            "date_from": "2022-03-10 12:03:57.108",
            "date_to": "2022-03-13 12:03:57.108",
            "recurring": False,
            "all_day": False,
            "color": "orange",
        },
        {
            "uuid": "4a6fb4e3-de96-42e6-bf61-63d47b3d89dd",
            "title": "Task #2",
            "desc": "Desc #2",
            "date_from": "2022-03-02 12:03:57.108",
            "date_to": "2022-03-20 13:03:57.108",
            "recurring": True,
            "all_day": False,
            "color": "red",
            "event": [
                {
                    "freq": "DAILY",
                    "interval": 1,
                    "date_from": "2022-03-02 12:03:57",
                    "date_to": "2022-03-10 13:03:57",
                    "at_mo": True,
                    "at_tu": None,
                    "at_we": None,
                    "at_th": None,
                    "at_fr": None,
                    "at_sa": None,
                    "at_su": None,
                },
                {
                    "freq": "DAILY",
                    "interval": 1,
                    "date_from": "2022-03-10 12:03:57",
                    "date_to": "2022-03-20 13:03:57",
                    "at_mo": None,
                    "at_tu": None,
                    "at_we": None,
                    "at_th": None,
                    "at_fr": None,
                    "at_sa": None,
                    "at_su": None,
                },
            ],
        },
        {
            "uuid": "d68146e0-a19e-4820-bac5-22c3f5b754e5",
            "title": "Task #3",
            "desc": "Desc #3",
            "date_from": "2022-03-10 12:03:57.108",
            "date_to": "2022-03-13 12:03:57.108",
            "recurring": False,
            "all_day": True,
            "color": "green",
        },
    ]

    print(events_dict)
    parse_non_recurring()

    calendar = []
    for event in events_dict:
        if event["recurring"] == False:
            start_raw = event["date_from"]
            end_raw = event["date_from"]

            temp_dict = {
                "uuid": uuid4(),
                "task_uuid": event["uuid"],
                "bgcolor": "orange",
                "title": event["title"],
                "details": event["desc"],
                "start": event["date_from"],
                "end": event["date_to"],
            }

            if event["all_day"] == False:
                temp_dict["time"] = "10:00"
                temp_dict["duration"] = "90"

            calendar.append(temp_dict)

        if event["recurring"] == True:
            for rule in event["event"]:

                freq_matrix = {"YEARLY": 0, "MONTHLY": 1, "WEEKLY": 2, "DAILY": 3}
                freq = freq_matrix[rule["freq"].upper()]

                days_matrix = [
                    rule["at_mo"],
                    rule["at_tu"],
                    rule["at_we"],
                    rule["at_th"],
                    rule["at_fr"],
                    rule["at_sa"],
                    rule["at_su"],
                ]

                days = list(itertools.compress([0, 1, 2, 3, 4, 5, 6], days_matrix))
                interval = rule["interval"]
                dt_start = datetime.strptime(rule["date_from"], "%Y-%m-%d %H:%M:%S")
                dt_end = datetime.strptime(rule["date_to"], "%Y-%m-%d %H:%M:%S")

                rule = rrule(freq=freq, interval=interval, byweekday=days, count=31, dtstart=dt_start, until=dt_end)
                gen_events = rule.between(after=start, before=end, inc=True)

                print(freq, days, interval, dt_start)

                for e in gen_events:
                    temp_dict = {
                        "uuid": uuid4(),
                        "task_uuid": event["uuid"],
                        "title": event["title"],
                        "desc": event["desc"],
                        "start": e,
                        "end": e,
                    }
                    if event["all_day"] == False:
                        temp_dict["time"] = "10:00"
                        temp_dict["duration"] = "90"

                    calendar.append(temp_dict)
                    print(e)

    return pendulum.now("Europe/Paris").format("HH:mm:ssZ")


def parse_non_recurring(data):
    start_raw = data["date_from"]
    end_raw = data["date_from"]

    temp_dict = {
        "uuid": uuid4(),
        "task_uuid": data["uuid"],
        "bgcolor": "orange",
        "title": data["title"],
        "details": data["description"],
        "start": data["date_from"],
        "end": data["date_to"],
    }

    if data["all_day"] == False:
        temp_dict["time"] = "10:00"
        temp_dict["duration"] = "90"

    return temp_dict


def parse_recurring(dt_from, dt_to, tsk, event):
    freq_matrix = {"YEARLY": 0, "MONTHLY": 1, "WEEKLY": 2, "DAILY": 3}
    freq = freq_matrix[event["freq"]]

    days_matrix = [
        event["at_mo"],
        event["at_tu"],
        event["at_we"],
        event["at_th"],
        event["at_fr"],
        event["at_sa"],
        event["at_su"],
    ]

    days = list(itertools.compress([0, 1, 2, 3, 4, 5, 6], days_matrix))
    interval = event["interval"]
    dt_start = event["date_from"]
    dt_end = event["date_to"]

    rule = rrule(freq=freq, interval=interval, byweekday=days, count=31, dtstart=dt_start, until=dt_end)
    gen_events = rule.between(after=pendulum.parse(dt_from), before=pendulum.parse(dt_to), inc=True)
    return gen_events
    # print(freq, days, interval, dt_start)


@event_router.get("/index", name="event:Index")  # response_model=List[TaskIndexResponse],
async def file_get_all(
    *,
    session: Session = Depends(get_session),
    dt_from="2022-03-01",
    dt_to="2022-03-28",
):

    # https://dateutil.readthedocs.io/en/stable/rrule.html

    # daily = rrule(freq=DAILY, interval=2, count=31, dtstart=dt_start)
    # workdays = rrule(freq=WEEKLY, byweekday=[0, 1, 2, 3, 4], count=31, dtstart=dt_start)
    # weekend = rrule(freq=WEEKLY, byweekday=[5, 6], count=31, dtstart=dt_start)
    # weekly = rrule(freq=WEEKLY, interval=2, byweekday=[5], count=31, dtstart=dt_start)
    # weekly_at_days = rrule(freq=WEEKLY, byweekday=[0, 2, 4], count=31, dtstart=dt_start)
    # monthly = rrule(freq=MONTHLY, interval=2, count=31, dtstart=dt_start)
    # yearly = rrule(freq=YEARLY, interval=2, count=31, dtstart=dt_start)

    # tasks = (
    #     session.exec(select(Tasks).options(joinedload(Tasks.events)).where(Tasks.date_from >= dt_from)).unique().all()
    # )

    tasks = session.exec(select(Tasks).where(Tasks.date_from >= dt_from)).all()

    calendar = []

    for task in tasks:
        if task.recurring == False:
            temp_dict = parse_non_recurring(task.dict())
            calendar.append(temp_dict)
        if task.recurring == True:
            tsk = task.dict()
            for event in task.events:
                event = event.dict()

                gen_events = parse_recurring(dt_from, dt_to, tsk, event)
                for e in gen_events:
                    temp_dict = {
                        "uuid": uuid4(),
                        "task_uuid": tsk["uuid"],
                        "title": tsk["title"],
                        "desc": tsk["description"],
                        "start": e,
                        "end": e,
                    }
                    if event["all_day"] == False:
                        temp_dict["time"] = "10:00"
                        temp_dict["duration"] = "90"
                    calendar.append(temp_dict)

    return calendar


@event_router.get("/{uuid}", name="event:Profile")
async def file_get_all(*, session: Session = Depends(get_session), dt_from="2022-03-01", dt_to="2022-03-28", uuid):

    task = session.exec(select(Tasks).where(Tasks.uuid == uuid)).one_or_none()
    calendar = []

    if task.recurring == False:
        temp_dict = parse_non_recurring(task.dict())
        calendar.append(temp_dict)
    if task.recurring == True:
        tsk = task.dict()
        for event in task.events:
            event = event.dict()

            gen_events = parse_recurring(dt_from, dt_to, tsk, event)
            for e in gen_events:
                temp_dict = {
                    "uuid": uuid4(),
                    "task_uuid": tsk["uuid"],
                    "title": tsk["title"],
                    "desc": tsk["description"],
                    "start": e,
                    "end": e,
                }
                if event["all_day"] == False:
                    temp_dict["time"] = "10:00"
                    temp_dict["duration"] = "90"
                calendar.append(temp_dict)

    return calendar


@event_router.get("/v/")
def event_valid():
    print("$$$$$$$$$$$$$$$$$$")
    data = {
        "month_day": "5522",
        "old_password": "asdf",
        "new_password": "@$#%$%$$#$#$#",
        "new_password_confirmation": "222322222",
        "phone": "0796359038",
        "birthday": "-2212-20",
        "email": "walid",
        "host": "172.30.30.20",
        "website": "www.oogle.com",
        "nationality": "afghan",
        "active": "1",
        "age": "12",
    }

    rules = {
        "month_day": r"required|regex:([a-zA-Z]+)",
        "birthday": "required|date_format:%m-%d-%Y|after:10-10-1995|before:02-25-2010|date",
        "old_password": "required",
        "new_password": "different:old_password|alpha|confirmed",
        "new_password_confirmation": "same:new_password",
        "phone": "phone|required|max:4|min:2|size:23",
        "email": "required|email|present",
        "host": "ip",
        "website": "website|size:",
        "nationality": "in:",
        "active": "boolean",
        "age": "between:18,66",
    }

    # my_messages = {
    #     "_comment": "You did not provide any field named <feld_name> in your data dictionary",
    #     "field_name.rule": "You did not provide any field named field_name in your data dictionary",
    #     "month_day.regex": "You did not provide any field named month_day in your data dictionary",
    #     "phone.max": "You did not provide any field named phone in your data dictionary",
    #     "month_day.required": "You did not provide any field named month_day in your data dictionary",
    #     "new_password_confirmation.same": "You did not provide any field named new_password_confirmation in your data dictionary",
    #     "phone.no_field": "You did not provide any field named phone in your data dictionary",
    #     "birthday.date_format": "You did not provide any field named birthday in your data dictionary",
    #     "new_password.alpha": "field new_password can only have alphabet values",
    #     "host.no_field": "You did not provide any field named host in your data dictionary",
    #     "email.no_field": "You did not provide any field named email in your data dictionary",
    #     "nationality.no_field": "You did not provide any field named nationality in your data dictionary",
    #     "active.no_field": "You did not provide any field named active in your data dictionary",
    #     "age.no_field": "You did not provide any field named age in your data dictionary",
    # }

    validation = Validation()

    errors = validation.validate(data, rules)

    for error in errors:
        print(error)
