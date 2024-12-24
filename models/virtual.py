from pydantic import BaseModel, Field
from typing import List

# Virtual Sport Model
class VirtualSport(BaseModel):
    id: str = Field(..., example="abc123")  # Field for object ID
    name: str = Field(..., example="Football")  # Name of the virtual sport
    odds: float = Field(..., example=1.75)  # Odds for the sport

    class Config:
        schema_extra = {
            "example": {
                "id": "abc123",
                "name": "Football",
                "odds": 1.75
            }
        }

# Virtual Sport Response Model
class VirtualSportResponse(BaseModel):
    sports: List[VirtualSport] = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "sports": [
                    {
                        "id": "abc123",
                        "name": "Football",
                        "odds": 1.75
                    },
                    {
                        "id": "def456",
                        "name": "Basketball",
                        "odds": 2.10
                    }
                ]
            }
        }
        
