# schemas/match.py
from pydantic import BaseModel, Field

class MatchBase(BaseModel):
    team_a: str
    team_b: str
    score: str
    status: str
    start_time: str

class MatchResponse(MatchBase):
    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True  # Use _id as the alias

class MatchCreate(MatchBase):
    pass

class MatchUpdate(MatchBase):
    pass
