from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime

class MatchCreate(BaseModel):
    home_team: str
    away_team: str
    start_time: str
    sport: str
    league: str
    odds: Dict[str, float]  # A dictionary for various betting odds

class MatchUpdate(BaseModel):
    home_team: Optional[str] = Field(default=None)
    away_team: Optional[str] = Field(default=None)
    start_time: Optional[str] = Field(default=None)
    sport: Optional[str] = Field(default=None)
    league: Optional[str] = Field(default=None)
    odds: Optional[Dict[str, float]] = Field(default=None)  # A dictionary for various betting odds

class MatchResponse(MatchCreate):
    id: str  # Returns the ObjectId as a string

    class Config:
        # Allow population of model fields using their aliases (if any)
        populate_by_name = True
        json_encoders = {
            # Add custom encoders if needed
        }
class MatchCreate(BaseModel):
    home_team: str
    away_team: str
    start_time: str
    sport: str
    league: str
    odds: Dict[str, float]  # A dictionary for various betting odds

class MatchUpdate(BaseModel):
    home_team: Optional[str] = Field(default=None)
    away_team: Optional[str] = Field(default=None)
    start_time: Optional[str] = Field(default=None)
    sport: Optional[str] = Field(default=None)
    league: Optional[str] = Field(default=None)
    odds: Optional[Dict[str, float]] = Field(default=None)

class MatchDetailResponse(MatchCreate):
    id: str  # Match identifier
    status: str  # Additional field to indicate the match status

class MatchResponse(MatchCreate):
    id: str  # Returns the ObjectId as a string

    class Config:
        populate_by_name = True
        json_encoders = {
            # Add custom encoders if needed
        }

class LiveMatchResponse(MatchDetailResponse):
    live_updates: List[Dict[str, str]]  # List of live updates for a match

class SportCategoryResponse(BaseModel):
    category_id: str
    name: str
    description: Optional[str] = None
    
class PlaceBetRequest(BaseModel):
    match_id: str
    amount: float = Field(..., gt=0, description="Amount to bet")
    team: str = Field(..., description="The team being bet on")

    class Config:
        schema_extra = {
            "example": {
                "match_id": "60c72b2f9c49ad1b4e0f0f32",
                "amount": 100.0,
                "team": "Team A"
            }
        }
    
class BetHistoryResponse(BaseModel):
    id: str
    user_id: str
    match_id: str
    bet_amount: float
    potential_win: float
    odds: float
    status: str  # e.g., "won", "lost", "pending"
    created_at: datetime