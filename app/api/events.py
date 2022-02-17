import json
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

event_router = APIRouter()


@event_router.get("/index", name="user:Profile")
async def file_get_all(*, session: Session = Depends(get_session)):
    uuid = "fd36ef87-f717-457b-a667-75d314edcd1d"
    event = session.exec(select(Events).where(Events.uuid == uuid)).one_or_none()

    task = session.exec(select(Tasks).where(Tasks.event_id == 6)).one_or_none()
    print(task.title)

    events = []
    details = {}
    details["title"] = task.title

    events.append(details)
    events.append({"title": "ONE", "desc": "Oh"})
    events.append({"title": "TWO", "desc": "Oh"})
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(json.dumps(events))

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

    # ev = dict(event)

    ev = event.dict()
    pp.pprint(ev)

    events = {}
    events["0"] = {}
    events["0"]["id"] = ev["id"]

    dt_start = ev["start_at"]
    dt_after = pendulum.from_format("2022-02-16 22", "YYYY-MM-DD HH", tz="Europe/Warsaw")
    dt_before = pendulum.from_format("2022-12-20 22", "YYYY-MM-DD HH", tz="Europe/Warsaw")

    if ev["unit"] == "YEARLY":
        freq = 0
    if ev["unit"] == "MONTHLY":
        freq = 1
    if ev["unit"] == "WEEKLY":
        freq = 2
    if ev["unit"] == "DAILY":
        freq = 3

    interval = ev["interval"]
    days = []
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

    rule = rrule(freq=freq, interval=interval, byweekday=days, count=31, dtstart=dt_start)
    times = rule.between(after=dt_after, before=dt_before, inc=True)
    print("##################")
    for t in times:
        print(t)
    print("##################")
    pp.pprint(events)

    # for ev in event:
    #     pp.pprint(ev.dict())

    # https://dateutil.readthedocs.io/en/stable/rrule.html

    # RRULE:FREQ=WEEKLY;BYDAY=TH # every Thursday
    # RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR # every Mon, Wed and Fri
    # RRULE:FREQ=WEEKLY;BYDAY=TU;INTERVAL=2 # every other Tuesday

    # Codziennie - rrule(freq=DAILY, count=31, dtstart=dt_start)
    # W dni robocze - rrule(freq=WEEKLY, byweekday=[0,1,2,3,4] count=31, dtstart=dt_start)
    # W weekend - rrule(freq=WEEKLY, byweekday=[5,6] count=31, dtstart=dt_start)
    # Co tydzień - rrule(freq=WEEKLY, byweekday=[5] count=31, dtstart=dt_start)
    # Co tydzień w dni: rrule(freq=WEEKLY, byweekday=[0,2,4] count=31, dtstart=dt_start)
    # Co miesiąc - rrule(freq=MONTHLY, count=31, dtstart=dt_start)
    # Co roku  - rrule(freq=YEARLY, count=31, dtstart=dt_start)

    dt_start = pendulum.from_format("2022-02-15 22", "YYYY-MM-DD HH", tz="Europe/Warsaw")
    dt_after = pendulum.from_format("2022-02-16 22", "YYYY-MM-DD HH", tz="Europe/Warsaw")
    dt_before = pendulum.from_format("2022-12-20 22", "YYYY-MM-DD HH", tz="Europe/Warsaw")

    daily = rrule(freq=DAILY, interval=2, count=31, dtstart=dt_start)
    workdays = rrule(freq=WEEKLY, byweekday=[0, 1, 2, 3, 4], count=31, dtstart=dt_start)
    weekend = rrule(freq=WEEKLY, byweekday=[5, 6], count=31, dtstart=dt_start)
    weekly = rrule(freq=WEEKLY, interval=2, byweekday=[5], count=31, dtstart=dt_start)
    weekly_at_days = rrule(freq=WEEKLY, byweekday=[0, 2, 4], count=31, dtstart=dt_start)
    monthly = rrule(freq=MONTHLY, interval=2, count=31, dtstart=dt_start)
    yearly = rrule(freq=YEARLY, interval=2, count=31, dtstart=dt_start)

    rule = daily

    times = rule.between(after=dt_after, before=dt_before, inc=True)
    print("##################")
    # for t in times:
    #     print(t)
    print("##################")

    return "OK"
