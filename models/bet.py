from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from datetime import datetime
from typing import Optional

class Bet(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    match_id: str
    bet_amount: float
    potential_win: float
    odds: float
    is_live: bool
    bet_status: str = "pending"  # Statuses: "pending", "won", "lost"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={ObjectId: str}
    )
