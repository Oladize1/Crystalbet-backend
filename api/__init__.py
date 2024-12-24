# api/__init__.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings  # Import configuration settings
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

app = FastAPI(
    title="Betting App API",
    description="This is the backend API for a betting platform built with FastAPI and MongoDB",
    version="1.0.0"
)

# Add CORS middleware to allow requests from different origins (frontend applications)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify allowed origins here for security purposes.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

# MongoDB connection setup
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.mongodb = app.mongodb_client[settings.MONGODB_DB]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# Include various API routes
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(bet_router, prefix="/api/bets", tags=["Bets"])
app.include_router(match_router, prefix="/api/matches", tags=["Matches"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(casino_router, prefix="/api/casino", tags=["Casino"])
app.include_router(virtuals_router, prefix="/api/virtuals", tags=["Virtuals"])
app.include_router(coupon_router, prefix="/api/coupons", tags=["Coupons"])
app.include_router(main_router, prefix="", tags=["Main"])

