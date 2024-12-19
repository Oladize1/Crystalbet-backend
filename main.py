from fastapi import FastAPI, HTTPException, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, List
from db.mongodb import init_db, close_db, get_collection
from core.config import settings
from logging_config import setup_logging, logger
import asyncio
import traceback,os

# Import routers
from api.auth import router as auth_router
from api.bets import router as bet_router
from api.match import router as match_router
from api.users import router as user_router
from api.admin import router as admin_router
from api.payments import router as payments_router
from api.transactions import router as transactions_router
from api.casino import router as casino_router
from api.virtuals import router as virtuals_router
from api.coupon import router as coupon_router
from api.main import router as main_router

# Initialize logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="CRYSTALBET API",
    description="API for betting, casino, virtual sports, and payment management.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection management
active_connections: List[WebSocket] = []

# WebSocket for live updates
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    active_connections.append(websocket)  # Add this connection to the list

    try:
        while True:
            # Fetch live data asynchronously
            live_data = await get_live_bets_data()  # Fetch data asynchronously
            await websocket.send_json(live_data)  # Send live data to the connected client
            
            # Send updates every 1 second
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        # Handle disconnection
        active_connections.remove(websocket)  # Remove from active connections
        logger.info(f"Client disconnected: {websocket.client}")
    
    except Exception as e:
        logger.error(f"Error with WebSocket connection: {e}")
        await websocket.close()  # Close the WebSocket connection

# Optionally, broadcast live data to all connected clients
async def broadcast_live_data(data: dict):
    # Send live data to all active WebSocket connections
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except WebSocketDisconnect:
            # Handle disconnection and clean up
            active_connections.remove(connection)
            logger.warning(f"Client disconnected during broadcast: {connection.client}")

# Health check endpoint with MongoDB connection status
@app.get("/health", tags=["Health"])
async def health_check():
    db_status = "Connected" if init_db else "Disconnected"
    return {"status": "Healthy", "message": f"API is up and running! MongoDB: {db_status}"}

# MongoDB connection management
@app.on_event("startup")
async def startup_db_client():
    await init_db()
    logger.info("Connected to MongoDB.")

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_db()
    logger.info("MongoDB connection closed.")

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error at {request.url}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(StarletteHTTPException)
async def not_found_error_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        logger.warning(f"404 Not Found at {request.url}")
        return JSONResponse(status_code=404, content={"error": "Resource not found"})
    return await http_exception_handler(request, exc)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unexpected error at {request.url}: {traceback.format_exc()}")
    return JSONResponse(status_code=500, content={"error": "An unexpected error occurred."})

# Dependency for admin content collection
async def get_content_collection() -> Any:
    return await get_collection("admin_content")

# Route to fetch all content
@app.get("/all-content", tags=["Content"])
async def get_all_content(content_collection: Any = Depends(get_content_collection), limit: int = 100):
    contents = await content_collection.find().to_list(limit)
    return contents

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(bet_router, prefix="/api/bets", tags=["Bets"])
app.include_router(match_router, prefix="/api/matches", tags=["Matches"])
app.include_router(user_router, prefix="/api/users", tags=["User Profile"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin CMS"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(casino_router, prefix="/api/casino", tags=["Casino"])
app.include_router(virtuals_router, prefix="/api/virtuals", tags=["Virtual Sports"])
app.include_router(coupon_router, prefix="/api/coupons", tags=["Coupon Check"])
app.include_router(main_router, tags=["General"])

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Betting Platform API!"}

# Live data fetching from MongoDB (or external service)
async def get_live_bets_data():
    # Example: Query live bets collection in MongoDB
    collection = await get_collection("live_bets")
    live_bets = await collection.find().to_list(100)  # Fetch live bets data asynchronously
    return live_bets


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    # uvicorn.run("main.app", host="0.0.0.0", port=port)