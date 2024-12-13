from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pymongo.collection import Collection
from bson import ObjectId
from pydantic import BaseModel, Field
# from pydantic import BaseSettings, SettingsConfigDict
from db.mongodb import get_db, get_collection  # Ensure you have the correct import for your MongoDB functions
from services.auth import verify_admin
from models.user import UserInDB

router = APIRouter(prefix="/admin", tags=["Admin"])

class ContentCreate(BaseModel):
    title: str
    description: str
    content_type: str = Field(..., description="Type of the content (e.g., 'article', 'announcement')")
    is_active: bool = True

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    is_active: Optional[bool] = None

class ContentResponse(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    description: str
    content_type: str
    is_active: bool

def content_to_response(content: dict) -> ContentResponse:
    return ContentResponse(
        id=str(content["_id"]),
        title=content["title"],
        description=content["description"],
        content_type=content["content_type"],
        is_active=content["is_active"],
    )

@router.get("/content", response_model=List[ContentResponse])
async def get_all_content(
    current_user: UserInDB = Depends(verify_admin),
    content_collection: Collection = Depends(lambda: get_collection("admin_content"))
):
    contents = await content_collection.find().to_list(None)
    return [content_to_response(content) for content in contents]

@router.post("/content", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate, 
    current_user: UserInDB = Depends(verify_admin),
    content_collection: Collection = Depends(lambda: get_collection("admin_content"))
):
    new_content = content_data.dict()
    insert_result = await content_collection.insert_one(new_content)
    
    if insert_result.inserted_id:
        created_content = await content_collection.find_one({"_id": insert_result.inserted_id})
        return content_to_response(created_content)
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Content creation failed")

@router.put("/content/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str, 
    content_data: ContentUpdate, 
    current_user: UserInDB = Depends(verify_admin),
    content_collection: Collection = Depends(lambda: get_collection("admin_content"))
):
    update_data = {k: v for k, v in content_data.dict(exclude_unset=True).items()}
    
    updated_content = await content_collection.find_one_and_update(
        {"_id": ObjectId(content_id)},
        {"$set": update_data},
        return_document=True
    )
    
    if updated_content:
        return content_to_response(updated_content)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

@router.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str, 
    current_user: UserInDB = Depends(verify_admin),
    content_collection: Collection = Depends(lambda: get_collection("admin_content"))
):
    delete_result = await content_collection.delete_one({"_id": ObjectId(content_id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    
    return None
