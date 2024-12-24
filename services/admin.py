from fastapi import HTTPException, status, Depends
from bson import ObjectId
from typing import List
from pymongo.collection import Collection
from core.security import get_current_admin
from models.admin import CMSContentModel
from schemas.admin import CMSContentCreate, CMSContentUpdate
from services.database import get_collection
from pydantic import BaseModel
from db.mongodb import get_db, get_collection

# Admin service class
class AdminService:
    def __init__(self, cms_collection: Collection):
        self.cms_collection = cms_collection

    async def get_all_content(self) -> List[CMSContentModel]:
        """Fetch all CMS content"""
        contents = self.cms_collection.find()
        return [CMSContentModel(**content) for content in contents]

    async def get_content_by_id(self, content_id: str) -> CMSContentModel:
        """Fetch a specific CMS content by ID"""
        if not ObjectId.is_valid(content_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content ID"
            )

        content = self.cms_collection.find_one({"_id": ObjectId(content_id)})
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
            )
        return CMSContentModel(**content)

    async def create_content(self, cms_data: CMSContentCreate, admin: BaseModel) -> CMSContentModel:
        """Create new CMS content (Admin only)"""
        content = cms_data.dict()
        content["created_by"] = admin.email  # Associate admin who created the content
        result = self.cms_collection.insert_one(content)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create content",
            )
        return CMSContentModel(**content, _id=str(result.inserted_id))

    async def update_content(self, content_id: str, cms_data: CMSContentUpdate, admin: BaseModel) -> CMSContentModel:
        """Update existing CMS content (Admin only)"""
        if not ObjectId.is_valid(content_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content ID"
            )

        content = self.cms_collection.find_one({"_id": ObjectId(content_id)})
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
            )

        update_data = cms_data.dict(exclude_unset=True)
        update_data["updated_by"] = admin.email  # Associate admin who updated the content

        result = self.cms_collection.update_one(
            {"_id": ObjectId(content_id)},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update content"
            )

        updated_content = self.cms_collection.find_one({"_id": ObjectId(content_id)})
        return CMSContentModel(**updated_content)

    async def delete_content(self, content_id: str) -> None:
        """Delete CMS content by ID (Admin only)"""
        if not ObjectId.is_valid(content_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content ID"
            )

        result = self.cms_collection.delete_one({"_id": ObjectId(content_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
            )
        return {"message": "Content deleted successfully"}

# Dependency function to get AdminService instance
def get_admin_service(cms_collection: Collection = Depends(get_collection)) -> AdminService:
    return AdminService(cms_collection=cms_collection)
