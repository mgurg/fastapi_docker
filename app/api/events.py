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

event_router = APIRouter()


@event_router.get("/index", name="user:Profile")
async def file_get_all(*, session: Session = Depends(get_session)):

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
    for t in times:
        print(t)
    print("##################")

    return "OK"
