import json
import os
import random
import requests as req
import youtube_dl

from typing import Dict, List

from fastapi import *
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models import Room

app = FastAPI()
VIDEO_DOWNLOAD_PATH = './static/music_files'  # 다운로드 경로
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:1234",
    "http://localhost:1234",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def homepage(request: Request):
    template = "index.html"
    context = {"request": request,
               "rooms": {room.room_code: str(room) for room in room_dict.values()}
               }
    return templates.TemplateResponse(template, context)


room_dict: Dict[str, Room] = {}


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
    context = {"request": request, "code": code}
    return templates.TemplateResponse(template, context)


@app.websocket("/chat/{code}/")
async def chat_room(code: str, websocket: WebSocket):
    room = room_dict.get(code)
    if room:
        await room.connect(websocket)
        while True:
            data = await websocket.receive_text()
            await room.broadcast(f"{data}")


@app.get("/search/{query}")
async def search(query: str):
    URL = f"https://www.googleapis.com/youtube/v3/search?q={query}&key=AIzaSyDlCe_en2fQZrQXEyV2hmDue9396qzaGrw"
    re = req.get(URL).json()
    item = re['items'][0]['id']['videoId']
    download_mp3(VIDEO_DOWNLOAD_PATH, item)

    return f"http://127.0.0.1:8000/static/music_files/{item}.mp3"


def download_mp3(output_dir, youtube_video_code):
    download_path = os.path.join(output_dir, '%(id)s.%(ext)s')
    video_url = 'https://www.youtube.com/watch?v=' + youtube_video_code

    # youtube_dl options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': download_path,  # 다운로드 경로 설정
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print('error', e)
