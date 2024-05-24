from apscheduler import Scheduler
from fastapi import FastAPI

scheduler = Scheduler()


def start_scheduler(app: FastAPI):
    @app.on_event("startup")
    def init_scheduler():
        # print("start scheduler...")
        scheduler.start_in_background()
        # print("start scheduler... DONE")
