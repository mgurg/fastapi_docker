from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.api.repository.generics import GenericRepo
from app.db import get_db
from app.models.models import Role, User

UserDB = Annotated[Session, Depends(get_db)]


class RoleRepo(GenericRepo[Role]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Role
        super().__init__(session, self.Model)

    def get_by_uuid(self, uuid: UUID) -> Role | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid)).options(selectinload("*"))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_role_by_name(self, name: str) -> Role | None:
        query = select(self.Model).where(func.lower(self.Model.role_title) == name.lower())

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_roles_summary(
            self,
            offset: int,
            limit: int,
            sort_column: str,
            sort_order: str,
            search: str | None = None,
            all: bool | None = None,
    ):
        base_query = (
            self.session.query(
                Role.uuid,
                Role.role_title,
                Role.role_description,
                Role.is_custom,
                func.count(User.id).label("count"),
                func.count(User.deleted_at).label("uncounted"),
            )
            .outerjoin(User, User.user_role_id == Role.id)
            .filter(Role.deleted_at.is_(None))
            .group_by(Role.uuid, Role.role_title, Role.role_description, Role.is_custom)
        )

        if search:
            search_filter = Role.role_title.ilike(f"%{search}%")
            base_query = base_query.filter(search_filter)

        if all is not None and not all:
            base_query = base_query.filter(Role.is_system == False)  # noqa: E712

        roles_query = base_query.order_by(text(f"{sort_column} {sort_order}")).offset(offset).limit(limit)
        result = self.session.execute(roles_query)

        # count_query = base_query.with_entities(func.count(Role.uuid))
        # count_result = self.session.execute(count_query)
        # total_records = count_result.scalar_one_or_none() or 0
        # Count query without grouping
        count_query = (
            self.session.query(func.count(Role.id))
            .outerjoin(User, User.user_role_id == Role.id)
            .filter(Role.deleted_at.is_(None))
        )

        if search:
            count_query = count_query.filter(search_filter)

        if all is not None and not all:
            count_query = count_query.filter(Role.is_system == False)  # noqa: E712

        count_result = self.session.execute(count_query)
        total_records = count_result.scalar_one_or_none() or 0

        return result.all(), total_records
