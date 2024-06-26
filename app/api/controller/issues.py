from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query

from app.api.service.issue_service import IssueService
from app.models.models import User
from app.schemas.responses import IssueResponse, ItemsPaginated
from app.service.bearer_auth import check_token

issue_test_router = APIRouter()

CurrentUser = Annotated[User, Depends(check_token)]
issueServiceDependency = Annotated[IssueService, Depends()]


# UserDB = Annotated[Session, Depends(get_session)]


@issue_test_router.get("", response_model=ItemsPaginated)
def issues_get_all(
    issue_service: issueServiceDependency,
    search: str | None = None,
    status: str = "active",
    user_uuid: UUID | None = None,
    priority: str | None = None,
    dateFrom: datetime | None = None,
    dateTo: datetime | None = None,
    tags: Annotated[list[UUID] | None, Query()] = None,
    limit: int = 10,
    offset: int = 0,
    field: Literal["created_at", "name", "priority", "status"] = "name",
    order: Literal["asc", "desc"] = "asc",
):
    db_items, count = issue_service.get_all(
        offset, limit, field, order, search, status, user_uuid, priority, dateFrom, dateTo, tags
    )

    return ItemsPaginated(data=db_items, count=count, offset=offset, limit=limit)


@issue_test_router.get("/export")
def get_export_issues(issue_service: issueServiceDependency, auth_user: CurrentUser):
    return issue_service.export()


@issue_test_router.get("/{issue_uuid}", response_model=IssueResponse)
def issue_get_one(
    issue_service: issueServiceDependency,
    issue_uuid: UUID,
    tenant: Annotated[str | None, Header()],
    auth_user: CurrentUser,
):
    issue = issue_service.get_issue_by_uuid(issue_uuid, tenant)

    return issue
