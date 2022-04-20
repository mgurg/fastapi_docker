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
from app.api.tasks import task_router
from app.api.user import user_router
from app.config import get_settings
from app.service.bearer_auth import has_token
from app.utils import get_secret

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
        dependencies=[Depends(has_token)],
        tags=["IDEA"],
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
app.add_middleware(SentryAsgiMiddleware)


@app.on_event("startup")
async def startup():
    logger.debug("That's it, beautiful and simple logging!")
    logger.info("🚀 Starting up and initializing app...")
    # Prime the push notification generator


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("⏳ Shutting down...")


@app.get("/push/{message}")
async def push_to_connected_websockets(message: str):
    await notifier.push(f"! Push notification: {message} !")


@app.get("/")
def read_root():
    # TODO: Health heck for DB & Storage
    # https://github.com/publichealthengland/coronavirus-dashboard-api-v2-server/blob/development/app/engine/healthcheck.py
    return {"Hello": "World", "time": datetime.utcnow(), "S": "srt"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    try:
        logger.debug("Get")
        # client = boto3.client("secretsmanager", region_name="eu-central-1")

        # response = client.get_secret_value(SecretId="amzn-db-credentials")
        # database_secrets = json.loads(response["SecretString"])
        secret = get_secret()
        logger.debug("secret")
        # logger.debug(f'{secret["port"]}')
    except Exception as ex:
        logger.error(f"### Secrets failed: {ex}")
        logger.error(traceback.format_exc())

    return {"item_id_no": item_id, "q": q}


if __name__ == "__main__":
    if settings.ENV == "production":
        uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=False, debug=False)
    else:
        uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True, debug=True)
