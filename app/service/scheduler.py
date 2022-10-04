from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from pytz import utc

from app.db import SQLALCHEMY_DATABASE_URL

scheduler = BackgroundScheduler()


def start_scheduler(app: FastAPI):
    @app.on_event("startup")
    def init_scheduler():
        jobstores = {"default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URL)}
        executors = {"default": ThreadPoolExecutor(1), "processpool": ProcessPoolExecutor(1)}
        job_defaults = {"coalesce": False, "max_instances": 1, "misfire_grace_time": 60}
        # scheduler = BackgroundScheduler(
        #     jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc
        # )
        scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

        print("start scheduler...")

        # scheduler.start()
        print("start scheduler... DONE")
