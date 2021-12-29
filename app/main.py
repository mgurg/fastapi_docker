# import asyncio
import asyncio
import random
from datetime import date, datetime, time
from typing import Dict, List, Optional
from uuid import UUID

import uvicorn

# requires `pip install aioaws`
from aioaws.s3 import S3Client, S3Config
from boto3.session import Session
from config.settings import get_settings
from fastapi import Cookie, Depends, FastAPI, File, Query, UploadFile, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from starlette.websockets import WebSocket, WebSocketDisconnect

settings = get_settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# https://github.com/tiangolo/fastapi/issues/258
# https://github.com/cthwaite/fastapi-websocket-broadcast/blob/master/app.py
class Notifier:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.active_users: Dict = {}
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            message = yield
            await self._notify(message)

    async def push(self, msg: str):
        await self.generator.asend(msg)

    async def connect(self, websocket: WebSocket, client_id: int):
        # if client_id != 123:
        #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

        await websocket.accept()
        self.connections.append(websocket)
        self.active_users[client_id] = websocket

    def remove(self, websocket: WebSocket, client_id: int):
        try:
            self.connections.remove(websocket)
            del self.active_users
        except KeyError as ex:
            print("No such key: '%s'" % ex.message)

    async def _notify(self, message: str):
        print(self.active_users)
        for connection in self.connections:
            await connection.send_text(message)
        # living_connections = []
        # while len(self.connections) > 0:
        #     # Looping like this is necessary in case a disconnection is handled
        #     # during await websocket.send_text(message)
        #     websocket = self.connections.pop()
        #     await websocket.send_text(message)
        #     living_connections.append(websocket)
        # self.connections = living_connections


notifier = Notifier()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await notifier.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        notifier.remove(websocket, client_id)


@app.get("/push/{message}")
async def push_to_connected_websockets(message: str):
    await notifier.push(f"! Push notification: {message} !")


@app.on_event("startup")
async def startup():
    # Prime the push notification generator
    await notifier.generator.asend(None)


@app.get("/")
def read_root():
    return {"Hello": "World", "time": datetime.utcnow()}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post("/upload/")
async def upload_aws_s3(file: UploadFile = File(...)):
    print(settings.s3_access_key, settings.s3_secret_access_key, settings.s3_region, settings.s3_bucket_name)

    ACCESS_KEY = settings.s3_access_key
    SECRET_KEY = settings.s3_secret_access_key

    session = Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    s3 = session.resource("s3")
    your_bucket = s3.Bucket(settings.s3_bucket_name)

    for s3_file in your_bucket.objects.all():
        print(s3_file.key)

    s3 = S3Client(
        AsyncClient,
        S3Config(
            settings.s3_access_key, settings.s3_secret_access_key, settings.s3_region, settings.s3_bucket_name + ".com"
        ),
    )
    await s3.upload("path/to/upload-to.txt", b"this the content")

    # files = [f for f in s3.list()]

    # # print(settings.s3_region)
    # print(settings.s3_access_key, settings.s3_secret_access_key, settings.s3_region, settings.s3_bucket_name)
    return {"region": settings.s3_region, "files": "files", "filename": file.filename}
    # return {"filename": file.filename}


if __name__ == "__main__":
    # if settings.ENV != "production":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True, debug=True)
# else:
#     uvicorn.run("main:app")
