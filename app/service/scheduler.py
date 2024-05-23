from fastapi import FastAPI
from apscheduler import Scheduler

scheduler = Scheduler()


def start_scheduler(app: FastAPI):
    @app.on_event("startup")
    def init_scheduler():
        # print("start scheduler...")
        scheduler.start_in_background()
        # print("start scheduler... DONE")
