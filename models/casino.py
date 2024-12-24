from pydantic import BaseModel, Field
from typing import Optional

# Base model containing common attributes for a casino game
class CasinoGameBase(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the casino game")
    description: Optional[str] = Field(None, description="Optional description of the game")
    category: str = Field(..., description="Category of the casino game (e.g., 'slots', 'table game', etc.)")
    image_url: Optional[str] = Field(None, description="URL to an image representing the casino game")

# Model for creating a new casino game
class CasinoGameCreate(CasinoGameBase):
    pass  # Inherits all fields from CasinoGameBase

# Model for updating an existing casino game
class CasinoGameUpdate(CasinoGameBase):
    pass  # Inherits all fields from CasinoGameBase

# Model for reading (fetching) a casino game, with an additional 'id' field
class CasinoGame(CasinoGameBase):
    id: str = Field(..., alias="_id", description="Unique identifier of the casino game")

    class Config:
        orm_mode = True  # This allows us to work with ORM-style data (e.g., MongoDB's ObjectId)
        allow_population_by_field_name = True  # Allows using '_id' instead of 'id' when creating a response

