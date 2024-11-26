from pydantic import BaseModel, Field, validator
from typing import Optional

class ItemModel(BaseModel):
    name: str = Field(..., example="Item name", description="Name of the item")
    description: Optional[str] = Field(None, example="Item description", description="A brief description of the item")
    price: float = Field(..., gt=0, example=19.99, description="Price of the item")

    # Validator to ensure the item name isn't too short
    @validator('name')
    def name_must_be_at_least_three_chars(cls, v):
        if len(v) < 3:
            raise ValueError('Item name must be at least 3 characters long')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sample Item",
                "description": "This is a sample item for demonstration purposes.",
                "price": 19.99
            }
        }
