from fastapi import APIRouter
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket
from app.web.auth.ws_deps import WsUserDep
from app.websocket.service import WsService

router = APIRouter(prefix="/chat", tags=["chat"])

ws_service = WsService()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user: WsUserDep):
    await ws_service.run(websocket)
