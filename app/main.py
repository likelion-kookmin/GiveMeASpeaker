import os
import random

from typing import Dict, List

from fastapi import FastAPI, Request, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from app.models import Room

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def homepage(request: Request):
    template = "index.html"
    context = {"request": request,
               "rooms": {room.room_code: str(room) for room in room_dict.values()}
               }
    return templates.TemplateResponse(template, context)


room_dict: Dict[str, Room] = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await notifier.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        notifier.remove(websocket)


def create_random_room_code():
    return str(random.randint(10 ** 5, 10 ** 6))


@app.post("/room/")
async def create_room():
    code = create_random_room_code()
    while code in room_dict:
        code = create_random_room_code()

    new_room = Room(room_code=code)
    await new_room.init()
    room_dict[code] = new_room
    
    print(room_dict)
    return {"code": code}


@app.get("/room")
def list_room(request: Request):
    print([str(room) for room in room_dict.values()])
    return [str(room) for room in room_dict.values()]


@app.get("/room/{code}")
def enter_room(request: Request, code: str):
    template = "room.html"
    context = {"request": request, "code":code}
    return templates.TemplateResponse(template, context)


@app.websocket("/chat/{code}/")
async def chat_room(code: str, websocket: WebSocket):
    room = room_dict.get(code)
    if room:
        await room.connect(websocket)
        while True:
            data = await websocket.receive_text()
            await room.broadcast(f"{data}")
