from uuid import uuid4

import sentry_sdk
from faker import Faker
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.api.auth import auth_router
from app.api.cc import cc_router
from app.api.files import file_router
from app.api.ideas import idea_router
from app.api.settings import setting_router
from app.api.users import user_router
from app.api.users_groups import group_router
from app.api.users_permissions import permission_router
from app.config import get_settings
from app.service.health_check import test_db
from app.service.scheduler import scheduler, start_scheduler
from app.service.tenants import alembic_upgrade_head, tenant_create

settings = get_settings()
# TODO: SentryFastapi Integration blocked by: https://github.com/getsentry/sentry-python/issues/1573
# sentry_sdk.init(dsn=settings.sentry_dsn, integrations=[SqlalchemyIntegration()])

logger.add("./app/logs/logs.log", format="{time} - {level} - {message}", level="DEBUG", backtrace=False, diagnose=True)


origins = ["http://localhost", "http://localhost:8080", "*"]


def create_application() -> FastAPI:
    """
    Create base FastAPI app with CORS middlewares and routes loaded
    Returns:
        FastAPI: [description]
    """
    app = FastAPI(debug=True)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["*"],
        max_age=86400,
    )

    app.include_router(auth_router, prefix="/auth", tags=["AUTH"])
    app.include_router(user_router, prefix="/users", tags=["USER"])
    app.include_router(permission_router, prefix="/permissions", tags=["PERMISSION"])
    app.include_router(group_router, prefix="/groups", tags=["USER_GROUP"])
    app.include_router(idea_router, prefix="/ideas", tags=["IDEA"])
    app.include_router(file_router, prefix="/files", tags=["FILE"])
    app.include_router(setting_router, prefix="/settings", tags=["SETTINGS"])
    app.include_router(cc_router, prefix="/cc", tags=["C&C"])
    return app


app = create_application()
# if settings.ENVIRONMENT == "PRD":
#     app.add_middleware(SentryAsgiMiddleware)

# if settings.ENVIRONMENT != "PRD":

#     @app.middleware("http")
#     async def add_sql_tap(request: Request, call_next):
#         profiler = SessionProfiler()
#         profiler.begin()
#         response = await call_next(request)
#         profiler.commit()
#         reporter = StreamReporter().report(f"{request.method} {request.url}", profiler.stats)
#         print(reporter)
#         return response


@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting up and initializing app...")
    await alembic_upgrade_head("public", "d6ba8c13303e")
    logger.info("🚀 Starting up and initializing app... DONE")
    # job = scheduler.add_job(myfunc, "interval", minutes=1)
    # scheduler.start()
    # jobs = scheduler.get_jobs()
    # print(jobs)
    logger.info("🚀 Starting up and initializing app... JOB")
    # job.remove()


def myfunc(text: str):
    logger.info("🚀 JOB" + text)
    print("JOB" + text)


start_scheduler(app)
job = scheduler.add_job(myfunc, args=["SDF"])
# scheduler.remove_job("e504b5a7bbc64df4a714105c919587bd")


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


@app.get("/", include_in_schema=False)
def read_root(request: Request):
    return {
        "Hello": "World",
        "tenant": request.headers.get("tenant", "public"),
        "env": settings.ENVIRONMENT,
    }


@app.get("/health")
def health_check():
    # https://github.com/publichealthengland/coronavirus-dashboard-api-v2-server/blob/development/app/engine/healthcheck.py
    # try:
    #     response = run_healthcheck()
    # except Exception as err:
    #     logger.exception(err)
    #     raise err
    # return response
    return {"status": "ok"}


@app.get("/health_db")
def health_check_db():
    return test_db()


@app.get("/fake_users")
def get_fake_users():
    faker = Faker()

    users = []
    for i in range(100):
        first_name = faker.first_name()
        last_name = faker.last_name()
        users.append({"uuid": str(uuid4()), "label": f"{first_name} {last_name}"})

    return users


@app.get("/fake_groups")
def get_fake_groups():
    faker = Faker()

    groups = []
    for i in range(20):
        company_name = faker.job()
        groups.append({"uuid": str(uuid4()), "label": company_name})

    return groups


@app.get("/create")
def read_item(schema: str):
    tenant_create(schema)
    # alembic_upgrade_head(schema)
    return {"schema": schema}


@app.get("/check_revision")
def check_revision(schema: str):
    # with with_db(schema) as db:
    #     context = MigrationContext.configure(db.connection())
    #     script = alembic.script.ScriptDirectory.from_config(alembic_config)
    #     if context.get_current_revision() != script.get_current_head():
    return {"ok": True}


# if __name__ == "__main__":
#     if settings.ENV == "production":
#         uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=False, debug=False)
#     else:
#         uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True, debug=True)
