import sentry_sdk
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.api.auth import auth_router
from app.api.users import user_router
from app.config import get_settings
from app.service.health_check import test_db
from app.service.tenants import alembic_upgrade_head, tenant_create

settings = get_settings()
sentry_sdk.init(dsn=settings.sentry_dsn, integrations=[SqlalchemyIntegration()])

logger.add("./app/logs/logs.log", format="{time} - {level} - {message}", level="DEBUG", backtrace=False, diagnose=True)


# -------------------------------------------------------

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
        auth_router,
        prefix="/auth",
        tags=["AUTH"],
    )

    app.include_router(
        user_router,
        prefix="/users",
        tags=["USER"],
    )

    return app


app = create_application()
if settings.ENVIRONMENT != "local":
    app.add_middleware(SentryAsgiMiddleware)


@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting up and initializing app...")
    alembic_upgrade_head("public", "d6ba8c13303e")
    logger.info("🚀 Starting up and initializing app... DONE")


@app.get("/")
def read_root(request: Request):
    return {"Hello": "World", "tenant": request.headers.get("tenant", "public")}


@app.get("/health")
async def health_check():
    # https://github.com/publichealthengland/coronavirus-dashboard-api-v2-server/blob/development/app/engine/healthcheck.py
    # try:
    #     response = await run_healthcheck()
    # except Exception as err:
    #     logger.exception(err)
    #     raise err
    # return response
    return {"status": "ok"}


@app.get("/health_db")
async def health_check_db():
    return await test_db()


@app.get("/create")
def read_item(schema: str):
    tenant_create(schema)
    # alembic_upgrade_head(schema)
    return {"schema": schema}


@app.get("/upgrade")
def upgrade_head(schema: str):
    # `_has_table("a")`
    alembic_upgrade_head(schema)
    return {"ok": True}


@app.get("/upgrade/all")
def upgrade_head_all(schema: str):

    return {"ok": True}


if __name__ == "__main__":
    if settings.ENV == "production":
        uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=False, debug=False)
    else:
        uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True, debug=True)
