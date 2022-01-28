# fastapi_docker/app/main.py
import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Optional
from urllib import response

# from loguru import logger
import boto3
import loguru
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.aws_s3 import s3_router
from app.api.register import register_router
from app.api.user import user_router
from app.config import get_settings
from app.utils import get_secret

log = logging.getLogger("uvicorn")
settings = get_settings()

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
        tags=["USER"],
    )

    app.include_router(
        user_router,
        prefix="/user",
        tags=["USER"],
    )

    app.include_router(
        s3_router,
        prefix="/s3",
        tags=["AWS_S3"],
    )

    return app


app = create_application()
logger = loguru.logger
logger.remove()
logger.add("./app/logs/logs.log", format="{time} - {level} - {message} ", level="DEBUG")


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


@app.on_event("startup")
async def startup():
    logger.debug("That's it, beautiful and simple logging!")
    log.info("🚀 Starting up and initializing app...")
    # Prime the push notification generator
    await notifier.generator.asend(None)


@app.on_event("shutdown")
async def shutdown_event():
    log.info("⏳ Shutting down...")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    # ws://0.0.0.0:5000/ws/1
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


@app.get("/")
def read_root():
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
