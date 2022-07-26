import argparse
import traceback

import sqlalchemy as sa
from alembic import command
from alembic.config import Config

from app.config import get_settings
from app.db import SQLALCHEMY_DATABASE_URL, with_db

settings = get_settings()


def alembic_upgrade_head(tenant_name, revision="head"):
    # set the paths values
    try:
        # create Alembic config and feed it with paths
        config = Config(str(settings.PROJECT_DIR / "alembic.ini"))
        config.set_main_option("script_location", str(settings.PROJECT_DIR / "migrations"))  # replace("%", "%%")
        config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
        config.cmd_opts = argparse.Namespace()  # arguments stub

        # If it is required to pass -x parameters to alembic
        x_arg = "tenant=" + tenant_name  # "dry_run=" + "True"
        if not hasattr(config.cmd_opts, "x"):
            if x_arg is not None:
                setattr(config.cmd_opts, "x", [])
                if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                    for x in x_arg:
                        config.cmd_opts.x.append(x)
                else:
                    config.cmd_opts.x.append(x_arg)
            else:
                setattr(config.cmd_opts, "x", None)

        # prepare and run the command
        revision = revision
        sql = False
        tag = None
        # command.stamp(config, revision, sql=sql, tag=tag)

        # upgrade command
        command.upgrade(config, revision, sql=sql, tag=tag)
    except Exception as e:
        print(e)
        print(traceback.format_exc())


def tenant_create(schema: str) -> None:
    try:
        with with_db("public") as db:
            db.execute(sa.schema.CreateSchema(schema))
            db.commit()
    except Exception as e:
        print(e)
