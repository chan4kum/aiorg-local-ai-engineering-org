from typing import Dict, Any, List
from fastapi import WebSocket
from opentelemetry import trace
import structlog

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

class NotificationService:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected", total_clients=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket client disconnected", total_clients=len(self.active_connections))

    async def broadcast(self, message: Dict[str, Any]):
        with tracer.start_as_current_span("notification.broadcast"):
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error("Failed to send message to client", error=str(e))
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn)
