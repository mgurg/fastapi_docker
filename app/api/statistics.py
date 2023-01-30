# Failures per machine

# SELECT events.resource_uuid, count(events.id) from piekarnia__cukiernia.events where action ='issue_add'
# group by events.resource_uuid;


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import pandas as pd 

from app.crud import crud_statistics
from app.db import get_db
from app.schemas.responses import StatsIssuesCounterResponse

# from app.schemas.schemas import IdeaIndexResponse
from app.service.bearer_auth import has_token

statistics_router = APIRouter()


@statistics_router.get("/issues_counter", response_model=StatsIssuesCounterResponse)
def stats_issues_counter(*, db: Session = Depends(get_db), auth=Depends(has_token)):
    issues_counter_summary = crud_statistics.get_issues_counter_summary(db)
    if not issues_counter_summary:
        return {"new": 0, "accepted": 0, "rejected": 0, "assigned": 0, "in_progress": 0, "paused": 0, "resolved": 0}

    issues_counter = dict(issues_counter_summary)

    for status in ["new", "accepted", "rejected", "assigned", "in_progress", "paused", "resolved"]:
        issues_counter.setdefault(status, 0)

    return issues_counter


@statistics_router.get("/first_steps")
def stats_first_steps(*, db: Session = Depends(get_db), auth=Depends(has_token)):

    user_id = auth["user_id"]
    response: dict = {}

    items = crud_statistics.get_items_counter_summary(db)
    items = dict(items)

    active = ["new", "accepted", "assigned", "in_progress", "paused"]
    inactive = ["rejected", "resolved"]

    issues_active = crud_statistics.get_issues_counter_by_status(db, active)
    issues_active = dict(issues_active)

    issues_inactive = crud_statistics.get_issues_counter_by_status(db, inactive)
    issues_inactive = dict(issues_inactive)

    response["items"] = {"total": sum(items.values()), "me": items.setdefault(user_id, 0)}
    response["users"] = crud_statistics.get_users_counter_summary(db, user_id)
    response["issues_active"] = {"total": sum(issues_active.values()), "me": issues_active.setdefault(user_id, 0)}
    response["issues_inactive"] = {"total": sum(issues_inactive.values()), "me": issues_inactive.setdefault(user_id, 0)}
    response["favourites"] = crud_statistics.get_favourites_counter_summary(db, user_id)

    return response


@statistics_router.get("/all_items_failures")
def stats_all_items_failures(*, db: Session = Depends(get_db), auth=Depends(has_token)):
    pass


@statistics_router.get("/events")
def stats_events_to_pd(*, db: Session = Depends(get_db), auth=Depends(has_token)):
   
    events = crud_statistics.get_events(db)

    columns=[
        "id","action","author_id"
        ]
    df_from_records = pd.DataFrame.from_records(events, index='id', columns=columns)
    
    print("########")
    print(df_from_records.head(5))
    print("########")

    return events
