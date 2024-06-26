from collections.abc import Sequence
from datetime import datetime, time, timezone
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Row
from sqlalchemy import func, not_, or_, select, text
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Issue, Tag, User

UserDB = Annotated[Session, Depends(get_db)]


class IssueRepo(GenericRepo[Issue]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Issue
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> Issue | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid)).options(selectinload("*"))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def count_by_type(self) -> Sequence[Row[tuple[Any, Any]]]:
        date_from = datetime.combine(datetime.now(timezone.utc), time.min)

        query = select(self.Model.status, func.count(self.Model.status)).group_by(self.Model.status)
        query = query.filter(func.DATE(self.Model.created_at) >= date_from)

        result = self.session.execute(query)
        return result.all()

    def count_by_status(self, status: list):
        query = (
            select(self.Model.author_id, func.count(self.Model.author_id))
            .where(self.Model.status.in_(status))
            .group_by(self.Model.author_id)
        )

        result = self.session.execute(query)
        return result.all()

    def count_by_tag(self, tag_id: int):
        query = select(func.count(self.Model.id)).filter(self.Model.tags_issue.any(Tag.id == tag_id))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_issues(self,
                   sort_column: str,
                   sort_order: str,
                   search: str | None,
                   status: str | None,
                   user_id: int | None,
                   priority: str | None,
                   date_from: datetime = None,
                   date_to: datetime = None,
                   tags: list[int] = None,
                   ):
        search_filters = []

        query = select(Issue)

        if search is not None:
            search_filters.append(Issue.name.ilike(f"%{search}%"))
            search_filters.append(Issue.text.ilike(f"%{search}%"))

            query = query.filter(or_(False, *search_filters))

        match status:
            case "all":
                ...
            case "active":
                query = query.where(not_(Issue.status.in_(["done", "rejected"])))
            case "inactive":
                query = query.where(Issue.status.in_(["done", "rejected"]))
            case "new" | "accepted" | "rejected" | "in_progress" | "paused" | "done" as issue_status:
                query = query.where(Issue.status == issue_status)

        match priority:
            case "low":
                query = query.where(self.Model.priority == "10")
            case "medium":
                query = query.where(self.Model.priority == "20")
            case "high":
                query = query.where(self.Model.priority == "30")
            case _:
                ...

        if user_id is not None:
            query = query.filter(Issue.users_issue.any(User.id == user_id))

        if date_from is not None:
            query = query.filter(func.DATE(Issue.created_at) >= date_from)

        if date_to is not None:
            query = query.filter(func.DATE(Issue.created_at) <= date_to)

        if tags is not None:
            query = query.where(Issue.tags_issue.any(Tag.id.in_(tags)))

        query = query.order_by(text(f"{sort_column} {sort_order}"))

        return query
