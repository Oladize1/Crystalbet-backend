from typing import Optional
from pydantic import BaseModel
from bson import ObjectId

# Helper function to parse ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class AZMenuModel(BaseModel):
    id: Optional[PyObjectId] = None
    name: str
    url: str

    class Config:
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string for JSON serialization
        }

class QuickLinksModel(BaseModel):
    id: Optional[PyObjectId] = None
    name: str
    url: str

    class Config:
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string for JSON serialization
        }

# Example usage
if __name__ == "__main__":
    # Create an example AZMenuModel instance
    az_menu = AZMenuModel(name="Home", url="/home")
    print(az_menu.json())  # Serialize to JSON

    # Create an example QuickLinksModel instance
    quick_link = QuickLinksModel(name="Google", url="https://www.google.com")
    print(quick_link.json())  # Serialize to JSON
