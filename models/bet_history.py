from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
from datetime import datetime
from db.mongodb import get_db

class BetHistory(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    match_id: str
    bet_amount: float
    potential_win: float
    odds: float
    status: str  # e.g., "won", "lost", "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    async def create(cls, bet_data: dict):
        from db.mongodb import get_db  # Local import to avoid circular import
        result = await get_db()["bets"].insert_one(bet_data)
        return cls(**bet_data)

    @classmethod
    async def get_all(cls, skip: int = 0, limit: int = 10):
        from db.mongodb import get_db  # Local import to avoid circular import
        bets = await get_db()["bets"].find().skip(skip).limit(limit).to_list(length=limit)
        return [cls(**bet) for bet in bets]

    @classmethod
    async def get_by_user_id(cls, user_id: str):
        from db.mongodb import get_db  # Local import to avoid circular import
        bets = await get_db()["bets"].find({"user_id": user_id}).to_list(length=100)
        return [cls(**bet) for bet in bets]
