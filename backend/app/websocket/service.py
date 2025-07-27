from typing import Callable
from app.websocket.schema import WsDataBase, WsEventBase
from starlette.websockets import WebSocket

class WsService:
    def __init__(self):
        self.actions = {}
        self.connect = None
        self.disconnect = None

    def on_connect(self):
        def wrapper(self, func: Callable):
            self.connect = func
            return func
        return wrapper
    
    def on_disconnect(self):
        def wrapper(self, func: Callable):
            self.disconnect = func
            return func
        return wrapper

    def on_event(self, event: str):
        def wrapper(self, func: Callable):
            self.actions[event] = func
            return func
        return wrapper
    
    async def run(self, websocket: WebSocket):
        while True:
            data = await websocket.receive_json()
            event = data.get("event")
            if event not in self.actions:
                continue
            await self.actions[event](data.get("data"))