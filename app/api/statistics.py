from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.crud import crud_statistics, crud_users
from app.db import get_db
from app.models.models import User
from app.schemas.responses import StatsIssuesCounterResponse

# from app.schemas.schemas import IdeaIndexResponse
from app.service.bearer_auth import has_token

statistics_router = APIRouter()

CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[Session, Depends(get_db)]


@statistics_router.get("/issues_counter", response_model=StatsIssuesCounterResponse)
def stats_issues_counter(*, db: UserDB, auth_user: CurrentUser):
    issues_counter_summary = crud_statistics.get_issues_counter_summary(db)
    if not issues_counter_summary:
        return {"new": 0, "accepted": 0, "rejected": 0, "assigned": 0, "in_progress": 0, "paused": 0, "done": 0}

    issues_counter = dict(issues_counter_summary)

    for status in ["new", "accepted", "rejected", "assigned", "in_progress", "paused", "done"]:
        issues_counter.setdefault(status, 0)

    return issues_counter


@statistics_router.get("/first_steps")
def stats_first_steps(*, db: UserDB, auth_user: CurrentUser):
    user_id = auth_user.id
    response: dict = {}

    items = crud_statistics.get_items_counter_summary(db)
    items = dict(items)

    active = ["new", "accepted", "assigned", "in_progress", "paused"]
    inactive = ["rejected", "done"]

    issues_active = crud_statistics.get_issues_counter_by_status(db, active)
    issues_active = dict(issues_active)

    issues_inactive = crud_statistics.get_issues_counter_by_status(db, inactive)
    issues_inactive = dict(issues_inactive)

    response["items"] = {"total": sum(items.values()), "me": items.setdefault(user_id, 0)}
    response["users"] = crud_users.get_user_count(db, user_id)
    response["issues_active"] = {"total": sum(issues_active.values()), "me": issues_active.setdefault(user_id, 0)}
    response["issues_inactive"] = {"total": sum(issues_inactive.values()), "me": issues_inactive.setdefault(user_id, 0)}
    response["favourites"] = crud_statistics.get_favourites_counter_summary(db, user_id)

    return response


@statistics_router.get("/all_items_failures")
def stats_all_items_failures(*, db: UserDB, auth_user: CurrentUser):
    pass


@statistics_router.get("/events")
def stats_events_to_pd(*, db: UserDB, auth_user: CurrentUser):
    events = crud_statistics.get_events(db)

    columns = ["id", "action", "author_id"]
    df_from_records = pd.DataFrame.from_records(events, index="id", columns=columns)

    print("########")
    print(df_from_records.head(5))
    print("########")

    df_from_records.info()

    output = df_from_records.to_csv(index=False)

    # https://stackoverflow.com/questions/61140398/fastapi-return-a-file-response-with-the-output-of-a-sql-query

    return StreamingResponse(
        iter([output]), media_type="text/csv", headers={"Content-Disposition": "attachment;filename=<file_name>.csv"}
    )
