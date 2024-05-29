from collections.abc import Sequence
from datetime import datetime, time, timezone
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session, selectinload

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Issue

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

    def get_issues_counter_by_status(self, status: list):
        query = (
            select(self.Model.author_id, func.count(self.Model.author_id))
            .where(self.Model.status.in_(status))
            .group_by(self.Model.author_id)
        )

        result = self.session.execute(query)
        return result.all()
