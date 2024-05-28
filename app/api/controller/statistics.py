from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.service.statistics_service import StatisticsService
from app.models.models import User
from app.schemas.responses import StatsIssuesCounterResponse
from app.service.bearer_auth import check_token

statistics_test_router = APIRouter()
CurrentUser = Annotated[User, Depends(check_token)]


@statistics_test_router.get("/issues_counter", response_model=StatsIssuesCounterResponse)
def count_issues_types(statistics_service: Annotated[StatisticsService, Depends()], auth_user: CurrentUser):
    return statistics_service.count_issues_types()


@statistics_test_router.get("/first_steps")
def stats_first_steps(statistics_service: Annotated[StatisticsService, Depends()], auth_user: CurrentUser):
    a = 1
    return statistics_service.first_steps(auth_user.id)
