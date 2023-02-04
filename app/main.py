import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.api.auth import auth_router
from app.api.cc import cc_router
from app.api.files import file_router
from app.api.guides import guide_router
from app.api.ideas import idea_router
from app.api.issues import issue_router
from app.api.items import item_router
from app.api.settings import setting_router
from app.api.statistics import statistics_router
from app.api.tags import tag_router
from app.api.users import user_router
from app.api.users_groups import group_router
from app.api.users_permissions import permission_router
from app.config import get_settings
from app.service.health_check import test_db
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

    app.include_router(item_router, prefix="/items", tags=["ITEM"])
    app.include_router(guide_router, prefix="/guides", tags=["GUIDE"])
    app.include_router(issue_router, prefix="/issues", tags=["ISSUE"])
    app.include_router(idea_router, prefix="/ideas", tags=["IDEA"])

    app.include_router(file_router, prefix="/files", tags=["FILE"])
    app.include_router(tag_router, prefix="/tags", tags=["TAG"])
    app.include_router(setting_router, prefix="/settings", tags=["SETTINGS"])
    app.include_router(statistics_router, prefix="/statistics", tags=["STATISTICS"])
    app.include_router(cc_router, prefix="/cc", tags=["C&C"])
    return app


app = create_application()
if settings.ENVIRONMENT == "PRD":
    # TODO: SentryFastapi Integration blocked by: https://github.com/getsentry/sentry-python/issues/1573
    sentry_sdk.init(dsn=settings.sentry_dsn, integrations=[SqlalchemyIntegration()])
    app.add_middleware(SentryAsgiMiddleware)

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
def startup():
    logger.info("🚀 [Starting up] Initializing DB data...")
    alembic_upgrade_head("public", "d6ba8c13303e")
    logger.info("🎽 [Job] Running test Job")


def myfunc(text: str):
    logger.info("👍 Job Message: " + text)
    logger.info("Waiting for first request ...")
    print("👍 Job Message: " + text)
    print("Waiting for first request ...")
    print()


start_scheduler(app)
job = scheduler.add_job(myfunc, args=["Everything OK, application is running correctly"])
# scheduler.remove_job("e504b5a7bbc64df4a714105c919587bd")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("👋 Bye!")
    print("👋 Bye!")
    # scheduler.shutdown()


@app.get("/", include_in_schema=False)
def read_root(request: Request):
    return {"Hello": "World", "tenant": request.headers.get("tenant", "public"), "env": settings.ENVIRONMENT}


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


# if __name__ == "__main__":
#     logger.info("Running APP locally (not docker)")
#     if settings.ENVIRONMENT == "PRD":
#         uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=False, debug=False)
#     else:
#         uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True, debug=True)
