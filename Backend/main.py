from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routes.alert_routes import router as alert_router
from routes.detection_routes import router as detection_router
from database import alerts_collection
from typing import List
import asyncio

app = FastAPI(
    title="Intelligent Public Area Monitoring System",
    description="Backend API for AI-powered public safety monitoring",
    version="1.0.0"
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(alert_router)
app.include_router(detection_router)

# ── WebSocket Manager ──────────────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        seen_alert_ids = set()
        while True:
            cursor = alerts_collection.find({"status": "Open"})
            async for doc in cursor:
                aid = doc["alert_id"]
                if aid not in seen_alert_ids:
                    seen_alert_ids.add(aid)
                    await websocket.send_json({
                        "event": "new_alert",
                        "alert_id": aid,
                        "type": doc["type"],
                        "severity": doc["severity"],
                        "camera_id": doc["camera_id"],
                        "description": doc["description"]
                    })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ── Health Check ───────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "running", "system": "Intelligent Public Area Monitoring System"}