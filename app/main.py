from typing import Any

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from loguru import logger
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.api.controller.auth import auth_test_router
from app.api.controller.files import file_test_router
from app.api.controller.issues import issue_test_router
from app.api.controller.items import item_test_router
from app.api.controller.permissions import permission_test_router
from app.api.controller.settings import setting_test_router
from app.api.controller.statistics import statistics_test_router
from app.api.controller.tags import tag_test_router
# from app.api.auth import auth_router
# from app.api.cc import cc_router
from app.api.controller.users import user_test_router
# from app.api.files import file_router
# from app.api.guides import guide_router
# from app.api.issues import issue_router
# from app.api.items import item_router
# from app.api.parts import part_router
# from app.api.settings import setting_router
# from app.api.statistics import statistics_router
# from app.api.tags import tag_router
from app.api.users import user_router
from app.api.users_permissions import permission_router
# from app.api.users_groups import group_router
# from app.api.users_permissions import permission_router
from app.config import get_settings
from app.service.health_check import run_healthcheck, check_required_tables
from app.service.scheduler import scheduler, start_scheduler
from app.service.tenants import alembic_upgrade_head

settings = get_settings()

logger.add("./app/logs/logs.log", format="{time} - {level} - {message}", level="DEBUG", backtrace=False, diagnose=True)

origins = ["http://localhost", "http://localhost:8080", "*"]


def create_application() -> FastAPI:
    """
    Create base FastAPI app with CORS middlewares and routes loaded
    Returns:
        FastAPI: [description]
    """
    app = FastAPI(debug=False)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["*"],
        max_age=86400,
    )

    # app.include_router(auth_router, prefix="/auth", tags=["AUTH"])
    app.include_router(user_router, prefix="/users", tags=["USER"])
    app.include_router(permission_router, prefix="/permissions", tags=["PERMISSION"])
    # app.include_router(group_router, prefix="/groups", tags=["USER_GROUP"])
    #
    # app.include_router(item_router, prefix="/items", tags=["ITEM"])
    # app.include_router(guide_router, prefix="/guides", tags=["GUIDE"])
    # app.include_router(issue_router, prefix="/issues", tags=["ISSUE"])
    # app.include_router(part_router, prefix="/parts", tags=["PART"])
    #
    # app.include_router(file_router, prefix="/files", tags=["FILE"])
    # app.include_router(tag_router, prefix="/tags", tags=["TAG"])
    # app.include_router(setting_router, prefix="/settings", tags=["SETTINGS"])
    # app.include_router(statistics_router, prefix="/statistics", tags=["STATISTICS"])
    # app.include_router(cc_router, prefix="/cc", tags=["C&C"])

    app.include_router(auth_test_router, prefix="/auth_test", tags=["TEST_A"])
    app.include_router(user_test_router, prefix="/user_test", tags=["TEST_U"])
    app.include_router(item_test_router, prefix="/item_test", tags=["TEST_I"])
    app.include_router(issue_test_router, prefix="/issue_test", tags=["TEST_ISSUES"])
    app.include_router(file_test_router, prefix="/file_test", tags=["TEST_FILES"])
    app.include_router(tag_test_router, prefix="/tag_test", tags=["TEST_TAGS"])
    app.include_router(setting_test_router, prefix="/settings_test", tags=["TEST_SETTINGS"])

    app.include_router(permission_test_router, prefix="/permission_test", tags=["TEST_P"])
    app.include_router(statistics_test_router, prefix="/statistics_test", tags=["TEST_S"])
    return app


app = create_application()
add_pagination(app)


def traces_sampler(sampling_context: dict[str, Any]) -> float:
    """Function to dynamically set Sentry sampling rates"""

    if settings.ENVIRONMENT != "PRD":
        return 0.0

    request_path = sampling_context.get("asgi_scope", {}).get("path")
    if request_path == "/health":
        # Drop all /health requests
        return 0.0
    return 0.1


if settings.ENVIRONMENT == "PRD":
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sampler=traces_sampler,
        profiles_sample_rate=0.1,
        integrations=[SqlalchemyIntegration()],
    )
    app.add_middleware(SentryAsgiMiddleware)


@app.on_event("startup")
def startup():
    logger.info("🚀 [Starting up] Initializing DB...")
    missing_tables = check_required_tables()

    if missing_tables:
        logger.info(f"Missing tables detected: {', '.join(missing_tables)}, Running Alembic upgrade...")
        alembic_upgrade_head("public", "d6ba8c13303e")
        logger.info("Alembic upgrade completed")
    else:
        logger.info("✅ All required tables present. Skipping Alembic upgrade.")
    logger.info("🎽 [Job] Running test Job")


def welcome_message(text: str):
    logger.info("👍 Job Message: " + text)
    logger.info("Waiting for first request ...")


start_scheduler(app)
job = scheduler.add_job(welcome_message, args=["Everything OK, application is running correctly"])


@app.on_event("shutdown")
def shutdown_event():
    logger.info("👋 Bye!")


@app.get("/", include_in_schema=False)
async def read_root(request: Request):
    return {"Hello": "World", "tenant": request.headers.get("tenant", "public"), "env": settings.ENVIRONMENT}

@app.get("/health")
def health_check():
    return run_healthcheck()
