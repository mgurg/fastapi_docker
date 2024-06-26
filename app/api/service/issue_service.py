import csv
import io
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import Depends, HTTPException
from loguru import logger
from starlette.responses import StreamingResponse
from starlette.status import HTTP_404_NOT_FOUND

from app.api.repository.FileRepo import FileRepo
from app.api.repository.IssueRepo import IssueRepo
from app.api.repository.ItemRepo import ItemRepo
from app.api.repository.TagRepo import TagRepo
from app.api.repository.UserRepo import UserRepo
from app.schemas.requests import IssueAddIn, IssueEditIn
from app.storage.storage_interface import StorageInterface
from app.storage.storage_service_provider import get_storage_provider


class IssueService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends()],
        issue_repo: Annotated[IssueRepo, Depends()],
        item_repo: Annotated[ItemRepo, Depends()],
        tag_repo: Annotated[TagRepo, Depends()],
        file_repo: Annotated[FileRepo, Depends()],
        storage_provider: Annotated[StorageInterface, Depends(get_storage_provider)],
    ) -> None:
        self.user_repo = user_repo
        self.issue_repo = issue_repo
        self.item_repo = item_repo
        self.tag_repo = tag_repo
        self.file_repo = file_repo
        self.storage_provider = storage_provider

    def get_all(
        self,
        offset: int,
        limit: int,
        sort_column: str,
        sort_order: str,
        search: str | None,
        status: str | None,
        user_uuid: UUID | None,
        priority: str | None,
        date_from: datetime = None,
        date_to: datetime = None,
        tags: list[UUID] = None,
    ):
        tag_ids = self.tag_repo.get_ids_by_tags_uuid(tags) if tags else None

        user_id = None
        if user_uuid is not None:
            db_user = self.user_repo.get_by_uuid(user_uuid)
            if db_user is None:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"User `{user_uuid}` not found")
            user_id = db_user.id

        db_issues, count = self.issue_repo.get_issues(
            offset, limit, sort_column, sort_order, search, status, user_id, priority, date_from, date_to, tag_ids
        )
        return db_issues, count

    def export(self):
        db_issues, count = self.issue_repo.get_issues(0, 50, "name", "asc", None, "all", None, None, None, None, None)

        f = io.StringIO()
        csv_file = csv.writer(f, delimiter=";")
        csv_file.writerow(["Symbol", "Name", "Description", "Author", "Status", "Created at"])
        for u in db_issues:
            csv_file.writerow([u.symbol, u.name, u.text, u.author_name, u.status, u.created_at])

        f.seek(0)
        response = StreamingResponse(f, media_type="text/csv")
        filename = f"issues_{datetime.today().strftime('%Y-%m-%d')}.csv"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    def get_issue_by_uuid(self, issue_uuid: UUID, tenant: str):
        db_issue = self.issue_repo.get_by_uuid(issue_uuid)
        if not db_issue:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Issue `{issue_uuid}` not found!")

        try:
            for picture in db_issue.files_issue:
                s3_folder_path = f"{tenant}/{picture.uuid}_{picture.file_name}"
                picture.url = self.storage_provider.get_url(s3_folder_path)
        except Exception as e:
            logger.error(e)

        return db_issue

    def add(self, issue: IssueAddIn, user_id: int, tenant: str):
        files = []
        if issue.files is not None:
            for file in issue.files:
                db_file = self.file_repo.get_by_uuid(file)
                if db_file:
                    files.append(db_file)

        tags = []
        if issue.tags is not None:
            for tag in issue.tags:
                db_tag = self.tag_repo.get_by_uuid(tag)
                if db_tag:
                    tags.append(db_tag)

        issue_uuid = str(uuid4())

        db_user = self.user_repo.get_by_id(user_id)

        db_item = self.item_repo.get_by_uuid(issue.item_uuid)
        item_id = None
        if db_item:
            item_id = db_item.id

        description = None
        if issue.text_html is not None:
            description = BeautifulSoup(issue.text_html, "html.parser").get_text()  # TODO add fix when empty

        last_issue_id = self.issue_repo.get_last_issue_id()
        issue_data = {
            "uuid": issue_uuid,
            "author_id": db_user.id,
            "author_name": f"{db_user.first_name} {db_user.last_name}",
            "item_id": item_id,
            "symbol": f"PR-{last_issue_id + 1}",
            "name": issue.name,
            "summary": issue.summary,
            "text": description,
            "text_json": issue.text_json,
            "files_issue": files,
            "tags_issue": tags,
            "color": issue.color,
            "priority": issue.priority,
            "status": "new",
            "created_at": datetime.now(timezone.utc),
        }

        new_issue = self.issue_repo.create(**issue_data)

        # Notification - TODO
        # email_users_list = crud_settings.get_users_list_for_email_notification(db, "all")  # empty: []
        # sms_users_list = []
        # if email_users_list or sms_users_list:
        #     notify_users(sms_users_list, email_users_list, new_issue)
        #
        # TODO:
        # event.create_new_basic_event(db, db_user, new_issue, "issue_add")
        # event.open_new_basic_summary(db, "issue", new_issue.uuid, "issueTotalTime")
        # event.open_new_basic_summary(db, "issue", new_issue.uuid, "issueResponseTime")

        return new_issue

    def edit(self, issue_uuid: UUID, issue: IssueEditIn) -> None:
        db_issue = self.issue_repo.get_by_uuid(issue_uuid)
        if not db_issue:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Issue `{issue_uuid}` not found!")

        issue_data = issue.model_dump(exclude_unset=True)

        if ("files" in issue_data) and (issue_data["files"] is not None):
            if len(issue_data["files"]) > 0:
                db_issue.files_issue.clear()
                for file in issue_data["files"]:
                    db_file = self.file_repo.get_by_uuid(file)
                    if db_file:
                        db_issue.files_issue.append(db_file)
            del issue_data["files"]

        if ("tags" in issue_data) and (issue_data["tags"] is not None):
            if len(issue_data["tags"]) > 0:
                db_issue.tags_issue.clear()
            for tag in issue_data["tags"]:
                db_tag = self.tag_repo.get_by_uuid(tag)
                if db_tag:
                    db_issue.tags_issue.append(db_tag)
            del issue_data["tags"]

        if ("users" in issue_data) and (issue_data["users"] is not None):
            if len(issue_data["tags"]) > 0:
                db_issue.users_issue.clear()
            for user in issue_data["users"]:
                db_user = self.user_repo.get_by_uuid(user)
                if db_user:
                    db_issue.users_issue.append(db_user)

            del issue_data["users"]

        if ("text_html" in issue_data) and (issue_data["text_html"] is not None):
            issue_data["text"] = BeautifulSoup(issue.text_html, "html.parser").get_text()
        del issue_data["text_html"]

        issue_data["updated_at"] = datetime.now(timezone.utc)

        self.issue_repo.update(db_issue.id, **issue_data)
        return None
