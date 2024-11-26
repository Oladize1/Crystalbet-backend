from bson import ObjectId
from db.mongodb import get_db  # Assuming you have your MongoDB connection setup

class UserService:
    @staticmethod
    async def get_user_by_id(user_id: str):
        from models.user import UserModel  # Lazy import to avoid circular import issue
        user = await get_db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return UserModel(**user)  # Return the Pydantic model instance
        return None

    @staticmethod
    async def update_user(user_id: str, user_update):
        from models.user import UserModel  # Lazy import to avoid circular import issue
        update_data = user_update.dict(exclude_unset=True)  # Only update provided fields
        result = await get_db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        if result.modified_count == 1:
            updated_user = await get_db.users.find_one({"_id": ObjectId(user_id)})
            return UserModel(**updated_user)  # Return the updated user
        return None
