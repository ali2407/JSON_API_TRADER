"""FastAPI main application"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio
import logging
from typing import List

from .database import init_db, get_db, SessionLocal
from .routers import trades, apikeys, analysis, market
from .services.sync_service import sync_service

logger = logging.getLogger(__name__)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("Starting Trading Terminal API...")
    init_db()
    print("Database initialized")

    # Run initial sync with BingX
    try:
        db = SessionLocal()
        print("Running initial trade sync with BingX...")
        sync_result = await sync_service.sync_all_trades(db)
        print(f"Sync complete: {sync_result}")
        db.close()
    except Exception as e:
        logger.error(f"Initial sync failed: {e}")
        print(f"Warning: Initial sync failed - {e}")

    # Start periodic sync in background (every 30 seconds)
    sync_service.start_periodic_sync(SessionLocal, interval=30)
    print("Periodic sync started (every 30s)")

    yield

    # Shutdown
    print("Shutting down Trading Terminal API...")
    sync_service.stop_periodic_sync()


# Create FastAPI app
app = FastAPI(
    title="Trading Terminal API",
    description="Backend API for automated trading terminal",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trades.router)
app.include_router(apikeys.router)
app.include_router(analysis.router)
app.include_router(market.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Trading Terminal API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()

            # Echo back or handle client messages
            await websocket.send_json({
                "type": "pong",
                "message": "Connection active"
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_trade_update(trade_data: dict):
    """Helper function to broadcast trade updates to all connected clients"""
    await manager.broadcast({
        "type": "trade_update",
        "data": trade_data
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
