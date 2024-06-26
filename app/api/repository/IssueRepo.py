from collections.abc import Sequence
from datetime import datetime, time, timezone
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Row, func, not_, or_, select, text
from sqlalchemy.orm import Session, selectinload

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

    def get_issues(
        self,
        offset: int,
        limit: int,
        sort_column: str,
        sort_order: str,
        search: str | None = None,
        status: str | None = None,
        user_id: int | None = None,
        priority: str | None = None,
        date_from: datetime = None,
        date_to: datetime = None,
        tags: list[int] = None,
    ) -> tuple[Sequence[Issue], int]:
        base_query = self.session.query(Issue).filter(Issue.deleted_at.is_(None)).options(selectinload("*"))

        if search:
            search_filter = or_(Issue.name.ilike(f"%{search}%"), Issue.text.ilike(f"%{search}%"))
            base_query = base_query.filter(search_filter)

        if status:
            match status:
                case "all":
                    pass
                case "active":
                    base_query = base_query.filter(not_(Issue.status.in_(["done", "rejected"])))
                case "inactive":
                    base_query = base_query.filter(Issue.status.in_(["done", "rejected"]))
                case "new" | "accepted" | "rejected" | "in_progress" | "paused" | "done" as issue_status:
                    base_query = base_query.filter(Issue.status == issue_status)

        if priority:
            match priority:
                case "low":
                    base_query = base_query.filter(Issue.priority == "10")
                case "medium":
                    base_query = base_query.filter(Issue.priority == "20")
                case "high":
                    base_query = base_query.filter(Issue.priority == "30")

        if user_id:
            user_filter = Issue.users_issue.any(User.id == user_id)
            base_query = base_query.filter(user_filter)

        if date_from:
            base_query = base_query.filter(func.DATE(Issue.created_at) >= date_from)

        if date_to:
            base_query = base_query.filter(func.DATE(Issue.created_at) <= date_to)

        if tags:
            tags_filter = Issue.tags_issue.any(Tag.id.in_(tags))
            base_query = base_query.filter(tags_filter)

        items_query = base_query.order_by(text(f"{sort_column} {sort_order}")).offset(offset).limit(limit)
        result = self.session.execute(items_query)

        count_query = base_query.with_entities(func.count(Issue.id))
        count_result = self.session.execute(count_query)
        total_records = count_result.scalar_one_or_none() or 0

        return result.scalars().all(), total_records
