import argparse
import re
from uuid import UUID

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from loguru import logger
from sentry_sdk import capture_exception
from unidecode import unidecode

from app.config import get_settings
from app.db import SQLALCHEMY_DB_URL, engine
from app.utils.decorators import timer

settings = get_settings()


@timer
def alembic_upgrade_head(tenant_name: str, revision="head", url: str = None):
    logger.info("🔺 [Schema upgrade] {tenant_name} to version: {revision}")

    if url is None:
        url = SQLALCHEMY_DB_URL
    try:
        # create Alembic config and feed it with paths
        config = Config(str(settings.PROJECT_DIR / "alembic.ini"))
        config.set_main_option("script_location", str(settings.PROJECT_DIR / "migrations"))  # replace("%", "%%")
        config.set_main_option("sqlalchemy.url", url)
        config.cmd_opts = argparse.Namespace()  # arguments stub

        # If it is required to pass -x parameters to alembic
        x_arg = "".join(["tenant=", tenant_name])  # "dry_run=" + "True"
        if not hasattr(config.cmd_opts, "x"):
            if x_arg is not None:
                config.cmd_opts.x = []
                if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                    for x in x_arg:
                        config.cmd_opts.x.append(x)
                else:
                    config.cmd_opts.x.append(x_arg)
            else:
                config.cmd_opts.x = None

        # prepare and run the command
        revision = revision
        sql = False
        tag = None
        # command.stamp(config, revision, sql=sql, tag=tag)

        # upgrade command
        command.upgrade(config, revision, sql=sql, tag=tag)
    except Exception as e:
        logger.error(e)
        # capture_exception(e)
        # print(traceback.format_exc())

    logger.info("✅ Schema upgraded for: " + tenant_name + " to version: " + revision)


# def tenant_create(schema: str) -> None:
#     logger.info("START create schema: " + schema)
#
#     try:
#         with with_db("public") as db:
#             db.execute(sa.schema.CreateSchema(schema))
#             db.commit()
#     except Exception as e:
#         logger.error(e)
#         capture_exception(e)
#     logger.info("Done create schema: " + schema)


@timer
def create_new_db_schema(schema: str) -> None:
    try:
        with engine.connect() as connection:
            connection.execute(sa.schema.CreateSchema(schema))
            connection.commit()
    except Exception as e:
        logger.error(f"New schema creation failed: {str(e)}")
        capture_exception(e)
    logger.info(f"🔩 New schema created: {schema}")


def delete_existing_db_schema(schema: str) -> None:
    logger.info("START DROP schema: " + schema)
    try:
        with engine.connect() as connection:
            connection.execute(sa.schema.DropSchema(schema, cascade=True))
            connection.commit()
    except Exception as e:
        capture_exception(e)
        logger.error(str(e))
    logger.info("Done DROP schema: " + schema)


def generate_tenant_id(name: str, uuid: UUID) -> str:
    company = re.sub("[^A-Za-z0-9 _]", "", unidecode(name))
    uuid = uuid.replace("-", "")

    return "".join([company[:28], "_", uuid]).lower().replace(" ", "_")
