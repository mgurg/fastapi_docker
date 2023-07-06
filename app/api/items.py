import csv
import io
import sys
from datetime import datetime, time, timezone
from typing import Annotated
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params, paginate
from sentry_sdk import capture_exception
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.crud import crud_auth, crud_files, crud_guides, crud_issues, crud_items, crud_qr, crud_users
from app.db import engine, get_db
from app.models.models import User
from app.schemas.requests import FavouritesAddIn, ItemAddIn, ItemEditIn
from app.schemas.responses import ItemIndexResponse, ItemResponse, StandardResponse
from app.service.aws_s3 import generate_presigned_url
from app.service.bearer_auth import has_token

item_router = APIRouter()
CurrentUser = Annotated[User, Depends(has_token)]
UserDB = Annotated[Session, Depends(get_db)]


@item_router.get("/", response_model=Page[ItemIndexResponse])
def item_get_all(
    *,
    db: UserDB,
    params: Annotated[Params, Depends()],
    auth_user: CurrentUser,
    search: str | None = None,
    user_uuid: UUID | None = None,
    field: str = "name",
    order: str = "asc",
):
    if field not in ["name", "created_at"]:
        field = "name"

    user_id = None
    if user_uuid is not None:
        db_user = crud_users.get_user_by_uuid(db, user_uuid)
        if db_user is None:
            raise HTTPException(status_code=401, detail="User not found")
        user_id = db_user.id

    db_items = crud_items.get_items(db, field, order, search, user_id)
    return paginate(db_items, params)


@item_router.get("/export")
def get_export_items(*, db: UserDB, auth_user: CurrentUser):
    db_items = crud_items.get_items(db, "name", "asc")

    f = io.StringIO()
    csv_file = csv.writer(f, delimiter=";")
    csv_file.writerow(["Name", "Description", "Symbol"])
    for u in db_items:
        csv_file.writerow([u.name, u.text, u.symbol])

    f.seek(0)
    response = StreamingResponse(f, media_type="text/csv")
    filename = f"items_{datetime.today().strftime('%Y-%m-%d')}.csv"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


# @item_router.post("/import")
# def get_import_users(*, db: Session = Depends(get_db), file: UploadFile | None = None, auth_user: CurrentUser):
#     if not file:
#         raise HTTPException(status_code=400, detail="No file sent")

#     csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"), delimiter=";")
#     data = {}
#     for idx, rows in enumerate(csvReader):
#         key = idx  # Assuming a column named 'Id' to be the primary key
#         data[key] = rows
#         data[key]["uuid"] = str(uuid4())
#         data[key]["is_active"] = True
#         data[key]["is_verified"] = True
#         data[key]["tz"] = "Europe/Warsaw"
#         data[key]["lang"] = "pl"
#         data[key]["phone"] = None
#         # print(rows)

#     file.file.close()

#     return data


@item_router.get("/{item_uuid}", response_model=ItemResponse)
def item_get_one(*, db: UserDB, item_uuid: UUID, request: Request, auth_user: CurrentUser):
    db_item = crud_items.get_item_by_uuid(db, item_uuid)

    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found!")

    try:
        for picture in db_item.files_item:
            picture.url = generate_presigned_url(
                request.headers.get("tenant", "public"), "_".join([str(picture.uuid), picture.file_name])
            )
    except Exception as e:
        capture_exception(e)

    return db_item


# @item_router.get("/timeline/{item_uuid}", response_model=list[EventTimelineResponse])
# def item_get_timeline_history(
#     *, db: Session = Depends(get_db), item_uuid: UUID, action: str | None = None, auth_user: CurrentUser
# ):
#     db_item = crud_items.get_item_by_uuid(db, item_uuid)
#     if not db_item:
#         raise HTTPException(status_code=400, detail="Item not found!")

#     db_events = crud_events.get_events_by_uuid_and_resource(db, item_uuid, action)
#     return db_events


@item_router.get("/statistics/all")  #
def item_get_statistics_all(
    *, db: UserDB, auth_user: CurrentUser, date_from: datetime | None = None, date_to: datetime | None = None
):
    issues_per_day = crud_issues.get_issues_by_day(db, date_from, date_to)
    issues_per_day_dict = {y.strftime("%Y-%m-%d"): x for y, x in issues_per_day}

    issues_per_hour = crud_issues.get_issues_by_hour(db, None, None)
    issues_per_hour_dict = {str(y): x for y, x in issues_per_hour}

    for hours in [time(i).strftime("%H") for i in range(24)]:
        issues_per_hour_dict.setdefault(hours, 0)

    issues_status = crud_issues.get_issues_status(db, date_from, date_to)
    issues_status_dict = dict(issues_status)

    for status in ["new", "accepted", "rejected", "assigned", "in_progress", "paused", "done"]:
        issues_status_dict.setdefault(status, 0)

    issues_status_dict = dict(sorted(issues_status_dict.items()))

    data = {
        "issuesCount": None,
        "issuesPerDay": None,
        "issuesPerHour": None,
        "issuesStatus": None,
        "repairTime": None,
        "users": None,
    }

    if issues_per_day_dict:
        data["issuesPerDay"] = issues_per_day_dict
    if issues_per_hour_dict:
        data["issuesPerHour"] = issues_per_hour_dict
    if issues_status_dict:
        data["issuesStatus"] = issues_status_dict
    return data


@item_router.get("/statistics/{item_uuid}")  #
def item_get_statistics(
    *,
    db: UserDB,
    item_uuid: UUID,
    auth_user: CurrentUser,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    issues_per_day_dict = None
    issues_per_hour_dict = None
    issues_status_dict = None
    issues_total_time_list = None
    issues_repair_time_list = None
    users = None

    try:
        db_item = crud_items.get_item_by_uuid(db, item_uuid)
        if not db_item:
            raise HTTPException(status_code=400, detail="Item not found!")

        db_issues_uuid: list[UUID] = crud_issues.get_item_issues_uuids(db, db_item.id)
        # db_issues_id: list[int] = crud_issues.get_item_issues_ids(db, db_item.id)

        issues_per_day = crud_issues.get_item_issues_by_day(db, [db_item.id], date_from, date_to)
        issues_per_day_dict = {y.strftime("%Y-%m-%d"): x for y, x in issues_per_day}

        issues_per_hour = crud_issues.get_item_issues_by_hour(db, [db_item.id], date_from, date_to)
        issues_per_hour_dict = {str(y): x for y, x in issues_per_hour}
        for hours in [time(i).strftime("%H") for i in range(24)]:
            issues_per_hour_dict.setdefault(hours, 0)
        issues_per_hour_dict = dict(sorted(issues_per_hour_dict.items()))

        issues_status = crud_issues.get_item_issues_status(db, [db_item.id], date_from, date_to)
        issues_status_dict = dict(issues_status)
        for status in ["new", "accepted", "rejected", "assigned", "in_progress", "paused", "done"]:
            issues_status_dict.setdefault(status, 0)

        issues_status_dict = dict(sorted(issues_status_dict.items()))

        issues_repair_time = crud_issues.get_mode_action_time(db, db_issues_uuid, "issueRepairTime")
        issues_repair_time_list = [item for tpl in issues_repair_time for item in tpl]

        issues_total_time = crud_issues.get_mode_action_time(db, db_issues_uuid, "issueTotalTime")
        issues_total_time_list = [item for tpl in issues_total_time for item in tpl]

        issue_assigned_users = crud_issues.get_assigned_users(db, db_issues_uuid)
        issue_assigned_users_list = [item for tpl in issue_assigned_users for item in tpl]
        issue_assigned_users_list = list(set(issue_assigned_users_list))

        users = {}
        for user_uuid in issue_assigned_users_list:
            user_details = crud_users.get_user_by_uuid(db, user_uuid)
            users["name"] = user_details.first_name + " " + user_details.last_name

    except Exception as e:
        line_no = sys.exc_info()[-1].tb_lineno
        file_name = sys.exc_info()[-1].tb_frame.f_code.co_filename
        type_name = type(e).__name__
        error_message = f"Error on line: {line_no}, file: {file_name}, type: {type_name}, message: " + str(e)
        print(error_message)
        # capture_exception(error_message)

    # średni czas potrzebny na podjęcie zgłoszenia

    data = {
        "issuesCount": None,
        "issuesPerDay": None,
        "issuesPerHour": None,
        "issuesStatus": None,
        "repairTime": None,
        "users": None,
    }

    if db_issues_uuid:
        data["issuesCount"] = len(db_issues_uuid)

    if issues_per_day_dict:
        data["issuesPerDay"] = issues_per_day_dict
    if issues_per_hour_dict:
        data["issuesPerHour"] = issues_per_hour_dict
    if issues_status_dict:
        data["issuesStatus"] = issues_status_dict
    if issues_total_time_list and len(issues_total_time_list) > 0:
        data["totalTime"] = {"max": issues_total_time_list[0], "avg": issues_total_time_list[1]}
    if issues_repair_time_list and len(issues_repair_time_list) > 0:
        data["repairTime"] = {"max": issues_repair_time_list[0], "avg": issues_repair_time_list[1]}
    if users:
        data["users"] = users

    return data


@item_router.post("/favourites", response_model=StandardResponse)
def item_add_to_favourites(*, db: UserDB, favourites: FavouritesAddIn, auth_user: CurrentUser):
    db_item = crud_items.get_item_by_uuid(db, favourites.item_uuid)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found!")

    for user in db_item.users_item:
        if user.uuid == favourites.user_uuid:
            db_item.users_item.remove(user)
            db.add(user)
            db.commit()
            return {"ok": True}

    db_user = crud_users.get_user_by_uuid(db, favourites.user_uuid)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    item_data = {"users_item": [db_user]}

    crud_items.update_item(db, db_item, item_data)

    return {"ok": True}


@item_router.post("/", response_model=ItemIndexResponse)
def item_add(*, db: UserDB, request: Request, item: ItemAddIn, auth_user: CurrentUser):
    tenant_id = request.headers.get("tenant", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Unknown Company!")

    company = None
    schema_translate_map = {"tenant": "public"}
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable) as public_db:
        company = crud_auth.get_public_company_by_tenant_id(public_db, tenant_id)
    if not company:
        raise HTTPException(status_code=400, detail="Unknown Company!")

    files = []
    if item.files is not None:
        for file in item.files:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

    item_uuid = str(uuid4())

    qr_code_id = crud_qr.generate_item_qr_id(db)
    qr_code_company = crud_qr.add_noise_to_qr(company.qr_id)

    qr_code_data = {
        "uuid": str(uuid4()),
        "resource": "items",
        "resource_uuid": item_uuid,
        "qr_code_id": qr_code_id,
        "qr_code_full_id": f"{qr_code_company}+{qr_code_id}",
        "ecc": "L",
        "created_at": datetime.now(timezone.utc),
    }

    new_qr_code = crud_qr.create_qr_code(db, qr_code_data)

    description = BeautifulSoup(item.text_html, "html.parser").get_text()

    item_data = {
        "uuid": item_uuid,
        "author_id": auth_user.id,
        "name": item.name,
        "symbol": item.symbol,
        "summary": item.summary,
        "text": description,
        "text_json": item.text_json,
        "qr_code_id": new_qr_code.id,
        "files_item": files,
        "created_at": datetime.now(timezone.utc),
    }

    new_item = crud_items.create_item(db, item_data)

    return new_item


@item_router.patch("/{item_uuid}", response_model=ItemIndexResponse)
def item_edit(*, db: UserDB, item_uuid: UUID, item: ItemEditIn, auth_user: CurrentUser):
    db_item = crud_items.get_item_by_uuid(db, item_uuid)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found!")

    item_data = item.dict(exclude_unset=True)

    files = []
    if ("files" in item_data) and (item_data["files"] is not None):
        for file in db_item.files_item:
            db_item.files_item.remove(file)
        for file in item_data["files"]:
            db_file = crud_files.get_file_by_uuid(db, file)
            if db_file:
                files.append(db_file)

        item_data["files_item"] = files
        del item_data["files"]

    if ("text_html" in item_data) and (item_data["text_html"] is not None):
        item_data["text"] = BeautifulSoup(item.text_html, "html.parser").get_text()

    item_data["updated_at"] = datetime.now(timezone.utc)

    new_item = crud_items.update_item(db, db_item, item_data)

    return new_item


@item_router.delete("/{item_uuid}", response_model=StandardResponse)
def item_delete(*, db: UserDB, item_uuid: UUID, auth_user: CurrentUser, force: bool = False):
    db_qr = crud_qr.get_qr_code_by_resource_uuid(db, item_uuid)
    db_item = crud_items.get_item_by_uuid(db, item_uuid)

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if force is False:
        crud_items.update_item(db, db_item, {"deleted_at": datetime.now(timezone.utc)})
        return {"ok": True}

    # TODO: Guides / Guides_Files

    print("DELETE files")
    for file in db_item.files_item:
        db_file = crud_files.get_file_by_uuid(db, file.uuid)
        print(db_file.file_name)

    print("DELETE guides")
    for guide in db_item.item_guides:
        crud_guides.get_guide_by_uuid(db, guide.uuid)

    db.delete(db_item)
    db.delete(db_qr)
    db.commit()

    return {"ok": True}
