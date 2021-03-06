# fastapi_docker/app/main.py
import traceback
from datetime import datetime
from typing import Dict, List, Optional

import sentry_sdk
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.api.aws_s3 import s3_router
from app.api.events import event_router
from app.api.files import file_router
from app.api.ideas import idea_router
from app.api.register import register_router
from app.api.settings import setting_router
from app.api.stats import stats_router
from app.api.tasks import task_router
from app.api.user import user_router
from app.config import get_settings
from app.service.bearer_auth import has_token
from app.service.health_check import run_healthcheck

logger.add("./app/logs/logs.log", format="{time} - {level} - {message}", level="DEBUG", backtrace=False, diagnose=True)

settings = get_settings()

sentry_sdk.init(dsn=settings.sentry_dsn, integrations=[SqlalchemyIntegration()])

origins = ["http://localhost", "http://localhost:8080", "*"]


def create_application() -> FastAPI:
    """
    Create base FastAPI app with CORS middlewares and routes loaded
    Returns:
        FastAPI: [description]
    """
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        register_router,
        prefix="/auth",
        tags=["REGISTER"],
    )

    app.include_router(
        user_router,
        prefix="/user",
        dependencies=[Depends(has_token)],
        tags=["USER"],
    )

    app.include_router(
        idea_router,
        prefix="/ideas",
        # dependencies=[Depends(has_token)],
        tags=["IDEA"],
    )
    app.include_router(
        setting_router,
        prefix="/settings",
        # dependencies=[Depends(has_token)],
        tags=["SETTING"],
    )

    app.include_router(
        stats_router,
        prefix="/stats",
        # dependencies=[Depends(has_token)],
        tags=["STATS"],
    )

    app.include_router(
        task_router,
        prefix="/tasks",
        dependencies=[Depends(has_token)],
        tags=["TASK"],
    )

    app.include_router(
        file_router,
        prefix="/files",
        tags=["FILE"],
    )

    app.include_router(
        event_router,
        prefix="/events",
        tags=["EVENT"],
    )

    # app.include_router(
    #     s3_router,
    #     prefix="/s3",
    #     tags=["AWS_S3"],
    # )

    return app


app = create_application()

if settings.environment != "local":
    app.add_middleware(SentryAsgiMiddleware)


@app.on_event("startup")
async def startup():

    logger.debug("That's it, beautiful and simple logging!")
    logger.info("APP ENVIRONMENT: ", settings.environment)
    logger.info("???? Starting up and initializing app...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("??? Shutting down...")


@app.get("/")
def read_root():
    return {"Hello": "World", "time": datetime.utcnow()}


@app.get("/health")
async def health_check():
    # https://github.com/publichealthengland/coronavirus-dashboard-api-v2-server/blob/development/app/engine/healthcheck.py
    try:
        response = await run_healthcheck()
    except Exception as err:
        logger.exception(err)
        raise err
    return response


@app.get("/items/")
def read_item():
    return {"mode": settings.environment}


if __name__ == "__main__":
    if settings.ENV == "production":
        uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=False, debug=False)
    else:
        uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True, debug=True)
