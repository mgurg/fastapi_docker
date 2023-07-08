import argparse
import configparser
import datetime
import gzip
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from tempfile import mkstemp

import boto3
from dotenv import load_dotenv
import psycopg
import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.table import Table

from app.config import get_settings

settings = get_settings()

console_app = typer.Typer(help="Postgres database management")

from enum import Enum


class Actions(str, Enum):
    list= 'list', 
    list_dbs = 'list_dbs'
    restore = 'restore', 
    backup = 'backup'

# from psycopg.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Amazon S3 settings.
# AWS_ACCESS_KEY_ID  in ~/.aws/credentials
# AWS_SECRET_ACCESS_KEY in ~/.aws/credentials


def upload_to_s3(file_full_path, dest_file, manager_config):
    """
    Upload a file to an AWS S3 bucket.
    """
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(
            file_full_path, manager_config.get("AWS_BUCKET_NAME"), manager_config.get("AWS_BUCKET_PATH") + dest_file
        )
        os.remove(file_full_path)
    except boto3.exceptions.S3UploadFailedError as exc:
        print(exc)
        exit(1)


def download_from_s3(backup_s3_key, dest_file, manager_config):
    """
    Upload a file to an AWS S3 bucket.
    """
    s3_client = boto3.resource("s3")
    try:
        s3_client.meta.client.download_file(manager_config.get("AWS_BUCKET_NAME"), backup_s3_key, dest_file)
    except Exception as e:
        print(e)
        exit(1)


def list_available_backups(storage_engine, manager_config):
    key_list = []
    backup_list = []
    if storage_engine == "LOCAL":
        try:
            backup_folder = manager_config.get("LOCAL_BACKUP_PATH")
            backup_list = os.listdir(backup_folder)
        except FileNotFoundError:
            print(f"Could not found {backup_folder} when searching for backups." f"Check your .config file settings")
            exit(1)
    elif storage_engine == "S3":
        # logger.info('Listing S3 bucket s3://{}/{} content :'.format(aws_bucket_name, aws_bucket_path))
        s3_client = boto3.client("s3")
        s3_objects = s3_client.list_objects_v2(Bucket=manager_config.get("AWS_BUCKET_NAME"),
                                               Prefix=manager_config.get("AWS_BUCKET_PATH")
                                               )
        backup_list = [s3_content["Key"] for s3_content in s3_objects["Contents"]]

    for bckp in backup_list:
        key_list.append(bckp)
    return key_list


def list_postgres_databases(host, database_name, port, user, password):
    try:
        process = subprocess.Popen(
            [
                "psql",
                "--dbname=postgresql://{}:{}@{}:{}/{}".format(user, password, host, port, database_name),
                "--list",
            ],
            stdout=subprocess.PIPE,
        )
        output = process.communicate()[0]
        if int(process.returncode) != 0:
            print(f"Command failed. Return code : {process.returncode}")
            exit(1)
        return output
    except Exception as e:
        print(e)
        exit(1)


def backup_postgres_db(host, database_name, port, user, password, dest_file, verbose):
    """
    Backup postgres db to a file.
    """
    if verbose:
        try:
            process = subprocess.Popen(
                [
                    "pg_dump",
                    "--dbname=postgresql://{}:{}@{}:{}/{}".format(user, password, host, port, database_name),
                    "-Fc",
                    "-f",
                    dest_file,
                    "-v",
                ],
                stdout=subprocess.PIPE,
            )
            output = process.communicate()[0]
            if int(process.returncode) != 0:
                print(f"Command failed. Return code : {process.returncode}")
                exit(1)
            return output
        except Exception as e:
            print(e)
            exit(1)
    else:
        try:
            process = subprocess.Popen(
                [
                    "pg_dump",
                    "--dbname=postgresql://{}:{}@{}:{}/{}".format(user, password, host, port, database_name),
                    "-f",
                    dest_file,
                ],
                stdout=subprocess.PIPE,
            )
            output = process.communicate()[0]
            if process.returncode != 0:
                print(f"Command failed. Return code : {process.returncode}")
                exit(1)
            return output
        except Exception as e:
            print(e)
            exit(1)


def compress_file(src_file):
    compressed_file = f"{str(src_file)}.gz"
    with open(src_file, "rb") as f_in:
        with gzip.open(compressed_file, "wb") as f_out:
            for line in f_in:
                f_out.write(line)
    return compressed_file


def extract_file(src_file):
    extracted_file, extension = os.path.splitext(src_file)

    with gzip.open(src_file, "rb") as f_in:
        with open(extracted_file, "wb") as f_out:
            for line in f_in:
                f_out.write(line)
    return extracted_file


def remove_faulty_statement_from_dump(src_file):
    temp_file, _ = tempfile.mkstemp()

    try:
        with open(temp_file, "w+"):
            process = subprocess.Popen(["pg_restore", "-l" "-v", src_file], stdout=subprocess.PIPE)
            output = subprocess.check_output(("grep", "-v", '"EXTENSION - plpgsql"'), stdin=process.stdout)
            process.wait()
            if int(process.returncode) != 0:
                print(f"Command failed. Return code : {process.returncode}")
                exit(1)

            os.remove(src_file)
            with open(src_file, "w+") as cleaned_dump:
                subprocess.call(["pg_restore", "-L"], stdin=output, stdout=cleaned_dump)

    except Exception as e:
        print(f"Issue when modifying dump : {e}")


def change_user_from_dump(source_dump_path, old_user, new_user):
    fh, abs_path = mkstemp()
    with os.fdopen(fh, "w") as new_file:
        with open(source_dump_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(old_user, new_user))
    # Remove original file
    os.remove(source_dump_path)
    # Move new file
    shutil.move(abs_path, source_dump_path)


def restore_postgres_db(db_host, db, port, user, password, backup_file, verbose):
    """Restore postgres db from a file."""
    try:
        subprocess_params = [
            "pg_restore",
            "--no-owner",
            "--dbname=postgresql://{}:{}@{}:{}/{}".format(user, password, db_host, port, db),
        ]

# pg_restore -a -t your_table /path/to/dump.sql

        if verbose:
            subprocess_params.append("-v")

        subprocess_params.append(backup_file)
        process = subprocess.Popen(subprocess_params, stdout=subprocess.PIPE)
        output = process.communicate()[0]

        if int(process.returncode) != 0:
            print(f"Command failed. Return code : {process.returncode}")

        return output
    except Exception as e:
        print(f"Issue with the db restore : {e}")


def create_db(db_host, database, db_port, user_name, user_password):
    try:
        con = psycopg.connect(dbname="postgres", port=db_port, user=user_name, host=db_host, password=user_password)

    except Exception as e:
        print(e)
        exit(1)

    # con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    con.autocommit = True
    cur = con.cursor()
    try:
        cur.execute(
            "SELECT pg_terminate_backend( pid ) "
            "FROM pg_stat_activity "
            "WHERE pid <> pg_backend_pid( ) "
            "AND datname = '{}'".format(database)
        )
        cur.execute("DROP DATABASE IF EXISTS {} ;".format(database))
    except Exception as e:
        print(e)
        exit(1)
    cur.execute("CREATE DATABASE {} ;".format(database))
    cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {database} TO {user_name} ;")
    return database


def swap_after_restore(db_host, restore_database, new_active_database, db_port, user_name, user_password):
    try:
        con = psycopg.connect(dbname="postgres", port=db_port, user=user_name, host=db_host, password=user_password)
        # con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        con.autocommit = True
        cur = con.cursor()
        cur.execute(
            "SELECT pg_terminate_backend( pid ) "
            "FROM pg_stat_activity "
            "WHERE pid <> pg_backend_pid( ) "
            "AND datname = '{}'".format(new_active_database)
        )
        cur.execute("DROP DATABASE IF EXISTS {}".format(new_active_database))
        cur.execute(f'ALTER DATABASE "{restore_database}" RENAME TO "{new_active_database}";')
    except Exception as e:
        print(e)
        exit(1)


def move_to_local_storage(comp_file, filename_compressed, manager_config):
    """Move compressed backup into {LOCAL_BACKUP_PATH}."""
    backup_folder = manager_config.get("LOCAL_BACKUP_PATH")
    try:
        os.listdir(backup_folder)
    except FileNotFoundError:
        os.mkdir(backup_folder)
    shutil.move(comp_file, f"{manager_config.get('LOCAL_BACKUP_PATH')}{filename_compressed}")


@console_app.command()
def main(configfile: str = typer.Option("", help="Database configuration file"),
         action: Actions = typer.Option(Actions.list , help="Action"),
         verbose: str = typer.Option("", help="Verbose output"),
         date: str = typer.Option("", help="Date to use for restore (show with --action list)"),
         dest_db :str = typer.Option(None, help="Name of the new restored database") 
         ):

# LOGGER
    logger = logging.getLogger(__name__)

    # the handler determines where the logs go: stdout/file
    shell_handler = RichHandler()
    file_handler = logging.FileHandler("debug.log")

    logger.setLevel(logging.DEBUG)
    shell_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)

    # the formatter determines what our logs will look like
    fmt_shell = '%(message)s'
    fmt_file = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'

    shell_formatter = logging.Formatter(fmt_shell, datefmt="[%X]")
    file_formatter = logging.Formatter(fmt_file)

    # here we hook everything together
    shell_handler.setFormatter(shell_formatter)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(shell_handler)
    logger.addHandler(file_handler)

# PATHS 
    # args_parser = argparse.ArgumentParser(description="Postgres database management")
    # args_parser.add_argument(
    #     "--action", metavar="action", choices=["list", "list_dbs", "restore", "backup"], required=True
    # )
    # args_parser.add_argument("--date", metavar="YYYY-MM-dd", help="Date to use for restore (show with --action list)")
    # args_parser.add_argument("--dest-db", metavar="dest_db", default=None, help="Name of the new restored database")
    # args_parser.add_argument("--verbose", default=False, help="Verbose output")
    # args_parser.add_argument("--configfile", required=True, help="Database configuration file")
    # args = args_parser.parse_args()

# ENV

    env_path = Path(settings.PROJECT_DIR, './app/.env')

    if env_path.is_file():
        load_dotenv(dotenv_path=env_path)

    config = configparser.ConfigParser()

    postgres_host: str = os.getenv("DB_HOST")
    postgres_port: str = os.getenv("DB_PORT")
    postgres_db: str = os.getenv("DB_DATABASE")
    postgres_restore = f"{postgres_db}_restore"
    postgres_user: str = os.getenv("DB_USERNAME")
    postgres_password: str = os.getenv("DB_PASSWORD")

    # config.read(Path(settings.PROJECT_DIR ,"./commands/db_backup/" , configfile))

    # postgres_host = config.get("postgresql", "host")
    # postgres_port = config.get("postgresql", "port")
    # postgres_db = config.get("postgresql", "db")
    # postgres_restore = f"{postgres_db}_restore"
    # postgres_user = config.get("postgresql", "user")
    # postgres_password = config.get("postgresql", "password")
    # aws_bucket_name = config.get("S3", "bucket_name")
    # aws_bucket_path = config.get("S3", "bucket_backup_path")
    storage_engine = "LOCAL" # config.get("setup", "storage_engine")
    timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"backup-{timestr}-{postgres_db}.dump"
    filename_compressed = f"{filename}.gz"
    restore_filename = "/tmp/restore.dump.gz"
    restore_uncompressed = "/tmp/restore.dump"
    cwd = os.getcwd()
    print("CWD: " + cwd)
    local_storage_path = Path(settings.PROJECT_DIR ,"./commands/db_backup/backups/")
    print("local_storage_path: " + str(local_storage_path))

    manager_config = {
        "AWS_BUCKET_NAME": "aws_bucket_name",
        "AWS_BUCKET_PATH": "aws_bucket_path",
        "BACKUP_PATH": "/tmp/",
        "LOCAL_BACKUP_PATH": str(local_storage_path),
    }

    local_file_path = f"{manager_config.get('BACKUP_PATH')}{filename}"

    # list task
    if action == "list":
        backup_objects = sorted(list_available_backups(storage_engine, manager_config), reverse=True)
        for key in backup_objects:
            logger.info(f"Key : {key}")
    # list databases task
    elif action == "list_dbs":
        result = list_postgres_databases(postgres_host, postgres_db, postgres_port, postgres_user, postgres_password)
        # for line in result.decode('utf-8').splitlines():
        #     logger.info(line)

        table_data = result.decode('utf-8').splitlines()
        columns = [x.strip() for x in table_data[1].split('|')]

        table = Table(title=table_data[0].strip())

        for column in columns:
            table.add_column(column.strip(), justify="right", style="cyan", no_wrap=True)

        for row in table_data[3:-2]:
            row_data = [x.strip() for x in row.split('|')]
            table.add_row(*row_data)


        console = Console()
        console.print(table)    
    # backup task
    elif action == "backup":
        logger.info(f"Backing up {postgres_db} database to {local_file_path}")
        result = backup_postgres_db(
            postgres_host, postgres_db, postgres_port, postgres_user, postgres_password, local_file_path, verbose
        )
        if verbose:
            for line in result.splitlines():
                logger.info(line)

        logger.info("Backup complete")
        logger.info(f"Compressing {local_file_path}")
        comp_file = compress_file(local_file_path)
        if storage_engine == "LOCAL":
            logger.info(f"Moving {comp_file} to local storage...")
            move_to_local_storage(comp_file, filename_compressed, manager_config)
            logger.info(f"Moved to {manager_config.get('LOCAL_BACKUP_PATH')}{filename_compressed}")
        elif storage_engine == "S3":
            logger.info(f"Uploading {comp_file} to Amazon S3...")
            upload_to_s3(comp_file, filename_compressed, manager_config)
            logger.info(f"Uploaded to {filename_compressed}")
    # restore task
    elif action == "restore":
        if not date:
            logger.warning(
                'No date was chosen for restore. Run again with the "list" ' "action to see available restore dates"
            )
        else:
            try:
                os.remove(restore_filename)
            except Exception as e:
                logger.info(e)
            all_backup_keys = list_available_backups(storage_engine, manager_config)
            backup_match = [s for s in all_backup_keys if date in s]
            if backup_match:
                logger.info(f"Found the following backup : {backup_match}")
            else:
                logger.error(f"No match found for backups with date : {date}")
                logger.info(f"Available keys : {[s for s in all_backup_keys]}")
                exit(1)

            if storage_engine == "LOCAL":
                logger.info(f"Choosing {backup_match[0]} from local storage")
                shutil.copy(f"{manager_config.get('LOCAL_BACKUP_PATH')}/{backup_match[0]}", restore_filename)
                logger.info("Fetch complete")
            elif storage_engine == "S3":
                logger.info(f"Downloading {backup_match[0]} from S3 into : {restore_filename}")
                download_from_s3(backup_match[0], restore_filename, manager_config)
                logger.info("Download complete")

            logger.info(f"Extracting {restore_filename}")
            ext_file = extract_file(restore_filename)
            # cleaned_ext_file = remove_faulty_statement_from_dump(ext_file)
            logger.info(f"Extracted to : {ext_file}")
            logger.info(f"Creating temp database for restore : {postgres_restore}")
            tmp_database = create_db(postgres_host, postgres_restore, postgres_port, postgres_user, postgres_password)
            logger.info(f"Created temp database for restore : {tmp_database}")
            logger.info("Restore starting")
            result = restore_postgres_db(
                postgres_host,
                postgres_restore,
                postgres_port,
                postgres_user,
                postgres_password,
                restore_uncompressed,
                verbose,
            )
            if verbose:
                for line in result.splitlines():
                    logger.info(line)
            logger.info("Restore complete")
            if dest_db is not None:
                restored_db_name = dest_db
                logger.info(
                    f"Switching restored database with new one : {postgres_restore} > {restored_db_name}"
                )
            else:
                restored_db_name = postgres_db
                logger.info(
                    f"Switching restored database with active one : {postgres_restore} > {restored_db_name}"
                )

            swap_after_restore(
                postgres_host, postgres_restore, restored_db_name, postgres_port, postgres_user, postgres_password
            )
            logger.info("Database restored and active.")
    else:
        logger.warning("No valid argument was given.")
        # logger.warning(args)


if __name__ == "__main__":
    console_app()
    # typer.run(main)
    # main()
