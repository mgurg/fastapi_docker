# import asyncio
import random
from typing import Optional

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("Accepting client connection...")
    await websocket.accept()
    while True:
        try:
            # Wait for any message from the client
            ws_text = await websocket.receive_text()
            if ws_text == "ping":
                await websocket.send_json({"ping": "pong"})
            else:
                # Send message to the client
                resp = {"value": random.uniform(0, 1)}
                # await asyncio.sleep(0.1)
                await websocket.send_json(resp)
        except Exception as e:
            print("error:", e)
            break
    print("Bye..")


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


# if __name__ == "__main__":
# if settings.ENV != "production":
# uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True, debug=True)
# else:
#     uvicorn.run("main:app")
