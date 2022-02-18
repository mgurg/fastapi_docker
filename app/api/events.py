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


@event_router.get("/index", name="event:Profile")
async def file_get_all(
    *,
    session: Session = Depends(get_session),
    dt_from="2022-02-01",
    dt_to="2022-02-28",
):
    task = session.exec(select(Tasks).where(Tasks.event_id.in_([1, 2]))).all()
    tsk_dict = {}
    tsk = list(task)
    for t in tsk:
        tsk_dict[t.event_id] = t.title
        print(t.event_id)
    print(tsk_dict)

    events_dict = []
    events = session.exec(select(Events).where(Events.start_at >= dt_from)).all()
    for event in events:
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

        dt_start = ev["start_at"]

        rule = rrule(freq=freq, interval=interval, byweekday=days, count=31, dtstart=dt_start)
        dt_after = pendulum.from_format(dt_from, "YYYY-MM-DD", tz="UTC")
        dt_before = pendulum.from_format(dt_to, "YYYY-MM-DD", tz="UTC")
        gen_events = rule.between(after=dt_after, before=dt_before, inc=True)

        for e in gen_events:
            details = {}
            details["title"] = tsk_dict[ev["id"]]
            # details["uuid"] = str(task.uuid)
            details["event_date"] = pendulum.instance(e, tz="UTC").to_iso8601_string()
            events_dict.append(details)

    # https://dateutil.readthedocs.io/en/stable/rrule.html

    # daily = rrule(freq=DAILY, interval=2, count=31, dtstart=dt_start)
    # workdays = rrule(freq=WEEKLY, byweekday=[0, 1, 2, 3, 4], count=31, dtstart=dt_start)
    # weekend = rrule(freq=WEEKLY, byweekday=[5, 6], count=31, dtstart=dt_start)
    # weekly = rrule(freq=WEEKLY, interval=2, byweekday=[5], count=31, dtstart=dt_start)
    # weekly_at_days = rrule(freq=WEEKLY, byweekday=[0, 2, 4], count=31, dtstart=dt_start)
    # monthly = rrule(freq=MONTHLY, interval=2, count=31, dtstart=dt_start)
    # yearly = rrule(freq=YEARLY, interval=2, count=31, dtstart=dt_start)

    return events_dict


@event_router.get("/{uuid}", name="event:Profile")
async def file_get_all(
    *,
    session: Session = Depends(get_session),
    dt_from="2022-02-01",
    dt_to="2022-02-28",
    uuid="bd426648-fd93-49bb-a363-904be5bf89f0",
):
    uuid = "bd426648-fd93-49bb-a363-904be5bf89f0"
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

    # ev = dict(event)
    # print("##################")
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(events_dict)
    # print("##################")

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

    # dt_start = pendulum.from_format("2022-02-15 22", "YYYY-MM-DD HH", tz="Europe/Warsaw")
    # dt_after = pendulum.from_format("2022-02-16 22", "YYYY-MM-DD HH", tz="Europe/Warsaw")
    # dt_before = pendulum.from_format("2022-12-20 22", "YYYY-MM-DD HH", tz="Europe/Warsaw")

    # daily = rrule(freq=DAILY, interval=2, count=31, dtstart=dt_start)
    # workdays = rrule(freq=WEEKLY, byweekday=[0, 1, 2, 3, 4], count=31, dtstart=dt_start)
    # weekend = rrule(freq=WEEKLY, byweekday=[5, 6], count=31, dtstart=dt_start)
    # weekly = rrule(freq=WEEKLY, interval=2, byweekday=[5], count=31, dtstart=dt_start)
    # weekly_at_days = rrule(freq=WEEKLY, byweekday=[0, 2, 4], count=31, dtstart=dt_start)
    # monthly = rrule(freq=MONTHLY, interval=2, count=31, dtstart=dt_start)
    # yearly = rrule(freq=YEARLY, interval=2, count=31, dtstart=dt_start)

    return events_dict
