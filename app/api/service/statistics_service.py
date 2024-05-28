from typing import Annotated

from fastapi import Depends

from app.api.repository.IssueRepo import IssueRepo
from app.api.repository.ItemRepo import ItemRepo
from app.api.repository.RoleRepo import RoleRepo
from app.api.repository.UserRepo import UserRepo


class StatisticsService:
    def __init__(
            self,
            user_repo: Annotated[UserRepo, Depends()],
            role_repo: Annotated[RoleRepo, Depends()],
            issue_repo: Annotated[IssueRepo, Depends()],
            item_repo: Annotated[ItemRepo, Depends()],
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.issue_repo = issue_repo
        self.item_repo = item_repo

    def count_issues_types(self):
        issues_counter_summary = self.issue_repo.count_by_type()
        if not issues_counter_summary:
            return {"new": 0, "accepted": 0, "rejected": 0, "assigned": 0, "in_progress": 0, "paused": 0, "done": 0}

        issues_counter = dict(issues_counter_summary)

        for status in ["new", "accepted", "rejected", "assigned", "in_progress", "paused", "done"]:
            issues_counter.setdefault(status, 0)

        return issues_counter

    def first_steps(self, user_id):
        response: dict = {}

        items = self.item_repo.get_items_counter_summary()
        items = dict(items)

        active = ["new", "accepted", "assigned", "in_progress", "paused"]
        inactive = ["rejected", "done"]

        issues_active = self.issue_repo.get_issues_counter_by_status(active)
        issues_active = dict(issues_active)

        issues_inactive = self.issue_repo.get_issues_counter_by_status(active)
        issues_inactive = dict(issues_inactive)

        response["items"] = {"total": sum(items.values()), "me": items.setdefault(user_id, 0)}
        response["users"] = self.user_repo.get_users_count(user_id)
        response["issues_active"] = {"total": sum(issues_active.values()), "me": issues_active.setdefault(user_id, 0)}
        response["issues_inactive"] = {"total": sum(issues_inactive.values()),
                                       "me": issues_inactive.setdefault(user_id, 0)}
        response["favourites"] = self.item_repo.get_favourites_counter_summary(user_id)

        return response
