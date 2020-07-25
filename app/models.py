import datetime

from typing import Dict, List
from fastapi import WebSocket
from pydantic import BaseModel


connections: Dict[str, List[WebSocket]] = {}


class Notifier:
    def __init__(self, target_socket: List[WebSocket]):
        self.connections = target_socket
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            message = yield
            await self._notify(message)

    async def push(self, msg: str):
        await self.generator.asend(msg)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def _notify(self, msg: str):
        alive_sockets = []
        while len(self.connections) > 0:
            print(self.connections)
            ws = self.connections.pop()
            try:
                await ws.send_text(msg)
                alive_sockets.append(ws)
            except RuntimeError:
                continue
        self.connections = alive_sockets


class Room:
    def __init__(self, room_code):
        self.created_at = datetime.datetime.now()
        self._room_code = room_code
        connections[self.room_code] = []
        self.room_connections = connections[self.room_code]
        self.notifier = Notifier(self.room_connections)

    def __str__(self):
        return f"Room#{self.room_code}, Time:{self.duration}"

    def __repr__(self):
        return f"Room#{self.room_code}, Time:{self.duration}"

    def __dict__(self):
        return {
            "room_code": self.room_code,
            "duration": self.duration
        }

    async def init(self):
        await self.notifier.generator.asend(None)

    @property
    def duration(self):
        return (datetime.datetime.now() - self.created_at).total_seconds()

    @property
    def room_code(self):
        return self._room_code

    async def broadcast(self, msg: str):
        await self.notifier.push(msg)

    async def connect(self, websocket: WebSocket):
        await self.notifier.connect(websocket)

    def disconnect(self, websocket: WebSocket):
        self.notifier.disconnect(websocket)
