from pydantic import BaseModel, ConfigDict
from bson import ObjectId

class AdminContentModel(BaseModel):
    id: str
    title: str
    description: str
    created_at: str
    updated_at: str

    # Pydantic v2: Use model_config and ConfigDict for settings
    model_config = ConfigDict(from_orm=True)

    # Optionally, you can include a validator for ObjectId if needed:
    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB data (with ObjectId) to a Pydantic model."""
        data['id'] = str(data['_id'])  # Convert ObjectId to string
        return cls(**data)

