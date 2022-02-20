import itertools
import json
import operator
import pprint
from datetime import datetime
from typing import List

import pendulum
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY, rrule, rrulestr
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models.models import Events, Tasks
from app.validation.validation import Validation

event_router = APIRouter()


@event_router.get("/index", name="event:Index")
async def file_get_all(
    *,
    session: Session = Depends(get_session),
    dt_from="2022-02-01",
    dt_to="2022-02-28",
):

    events_dict = []
    events = session.exec(select(Events).where(Events.start_at >= dt_from)).all()

    # Task details
    ids = []
    for event in events:
        ids.append(event.id)
    task = session.exec(select(Tasks).where(Tasks.event_id.in_(ids))).all()  # chainMap

    tsk_dict = {}
    for t in list(task):
        tsk_dict[t.event_id] = t.dict()
    #

    for event in events:
        id = event.id
        event = event.dict()

        frequency = {0: "YEARLY", 1: "MONTHLY", 2: "WEEKLY", 3: "DAILY"}

        # days = [0, 1, 2, 3, 4, 5, 6]
        # d = [True, False, True, False, True, False, True]
        # e = zip(*itertools.compress(days, d))
        # print(e)

        if event["unit"] == "YEARLY":
            freq = 0
        if event["unit"] == "MONTHLY":
            freq = 1
        if event["unit"] == "WEEKLY":
            freq = 2
        if event["unit"] == "DAILY":
            freq = 3

        interval = event["interval"]

        days = []
        if event["at_mo"] == True:
            days.append(0)
        if event["at_tu"] == True:
            days.append(1)
        if event["at_we"] == True:
            days.append(2)
        if event["at_th"] == True:
            days.append(3)
        if event["at_fr"] == True:
            days.append(4)
        if event["at_sa"] == True:
            days.append(5)
        if event["at_su"] == True:
            days.append(6)

        dt_start = event["start_at"]

        # https://dateutil.readthedocs.io/en/stable/rrule.html

        # daily = rrule(freq=DAILY, interval=2, count=31, dtstart=dt_start)
        # workdays = rrule(freq=WEEKLY, byweekday=[0, 1, 2, 3, 4], count=31, dtstart=dt_start)
        # weekend = rrule(freq=WEEKLY, byweekday=[5, 6], count=31, dtstart=dt_start)
        # weekly = rrule(freq=WEEKLY, interval=2, byweekday=[5], count=31, dtstart=dt_start)
        # weekly_at_days = rrule(freq=WEEKLY, byweekday=[0, 2, 4], count=31, dtstart=dt_start)
        # monthly = rrule(freq=MONTHLY, interval=2, count=31, dtstart=dt_start)
        # yearly = rrule(freq=YEARLY, interval=2, count=31, dtstart=dt_start)

        rule = rrule(freq=freq, interval=interval, byweekday=days, count=31, dtstart=dt_start)
        dt_after = pendulum.from_format(dt_from, "YYYY-MM-DD", tz="UTC")
        dt_before = pendulum.from_format(dt_to, "YYYY-MM-DD", tz="UTC")
        gen_events = rule.between(after=dt_after, before=dt_before, inc=True)

        for e in gen_events:
            details = {}
            details["title"] = tsk_dict[id]["title"]
            details["description"] = tsk_dict[id]["description"]
            details["uuid"] = str(tsk_dict[id]["uuid"])
            details["event_date"] = pendulum.instance(e, tz="UTC").to_iso8601_string()
            events_dict.append(details)

    return events_dict


@event_router.get("/{uuid}", name="event:Profile")
async def file_get_all(*, session: Session = Depends(get_session), dt_from="2022-02-01", dt_to="2022-02-28"):
    uuid = "4a6fb4e3-de96-42e6-bf61-63d47b3d89dd"
    task = session.exec(select(Tasks).where(Tasks.uuid == uuid)).one_or_none()
    event = session.exec(select(Events).where(Events.id == task.event_id)).one_or_none()
    ev = event.dict()

    if ev["unit"] == "YEARLY":
        freq = 0
    if ev["unit"] == "MONTHLY":
        freq = 1
    if ev["unit"] == "WEEKLY":
        freq = 2
    if ev["unit"] == "DAILY":
        freq = 3

    interval = ev["interval"]

    if ev["at_mo"] == True:
        days.append(0)
    if ev["at_tu"] == True:
        days.append(1)
    if ev["at_we"] == True:
        days.append(2)
    if ev["at_th"] == True:
        days.append(3)
    if ev["at_fr"] == True:
        days.append(4)
    if ev["at_sa"] == True:
        days.append(5)
    if ev["at_su"] == True:
        days.append(6)

    dt_start = ev["start_at"]

    rule = rrule(freq=freq, interval=interval, byweekday=days, count=31, dtstart=dt_start)
    dt_after = pendulum.from_format(dt_from, "YYYY-MM-DD", tz="UTC")
    dt_before = pendulum.from_format(dt_to, "YYYY-MM-DD", tz="UTC")
    gen_events = rule.between(after=dt_after, before=dt_before, inc=True)

    events_dict = []

    for e in gen_events:
        details = {}
        details["title"] = task.title
        details["uuid"] = str(task.uuid)
        details["event_date"] = pendulum.instance(e, tz="UTC").to_iso8601_string()
        events_dict.append(details)

    #   events: [
    # {
    #   title: '1st of the Month',
    #   details: 'Everything is funny as long as it is happening to someone else',
    #   date: getCurrentDay(1),
    #   bgcolor: 'orange'
    # },
    # {
    #   title: 'Sisters Birthday',
    #   details: 'Buy a nice present',
    #   date: getCurrentDay(4),
    #   bgcolor: 'green',
    #   icon: 'fas fa-birthday-cake'
    # },

    # https://dateutil.readthedocs.io/en/stable/rrule.html

    return events_dict


@event_router.get("/valid", name="event:Valid")
async def event_valid():
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
