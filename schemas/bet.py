from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BetCreate(BaseModel):
    match_id: str
    odds: float
    stake: float

class Bet(BaseModel):
    id: str
    match_id: str
    odds: float
    stake: float
    user_id: str
    status: str = Field(default="pending")  # default status

class BetOut(Bet):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class BetSlip(BaseModel):
    bets: List[Bet]
    total_stake: float
    potential_payout: float

class BetFilter(BaseModel):
    odds_less_than: Optional[float] = None
    status: Optional[str] = None
    
class BetHistoryResponse(BaseModel):
    id: str
    user_id: str
    match_id: str
    bet_amount: float
    potential_win: float
    odds: float
    status: str  # e.g., "won", "lost", "pending"
    created_at: datetime
class PlaceBetRequest(BaseModel):
    match_id: str  # Match ID the user is betting on
    odds: float  # The odds for the match at the time of betting
    amount: float  # The stake amount for the bet

    class Config:
        schema_extra = {
            "example": {
                "match_id": "60b6e6cdb3b27f001c8d3f8a",
                "odds": 2.5,
                "amount": 100.0
            }
        }    
