import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from backend.dependencies import get_event_bus
from services.event_bus import EventBus

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, event_bus: EventBus = Depends(get_event_bus)):
    await manager.connect(websocket)
    
    # We create a callback to handle events from the event bus
    async def event_handler(event_data: dict):
        await manager.broadcast(json.dumps(event_data))

    # Subscribe to interesting events
    subscription_id = await event_bus.subscribe("project.*", event_handler)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WS messages if necessary
            # e.g. await event_bus.publish("ws.message", {"data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await event_bus.unsubscribe(subscription_id)
