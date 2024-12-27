from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from typing import Any, List, Optional
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Validate that environment variables are loaded
if not MONGO_URI or not DATABASE_NAME:
    logging.error("MONGO_URI and DATABASE_NAME must be set in the .env file.")
    raise ValueError("MONGO_URI and DATABASE_NAME must be set in the .env file.")

# Global MongoDB client and database reference
client: Optional[AsyncIOMotorClient] = None
database: Optional[Any] = None

# Initialize MongoDB connection with logging
async def init_db():
    global client, database
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        database = client[DATABASE_NAME]
        logging.info(f"Connected to MongoDB: {DATABASE_NAME}")
    except PyMongoError as e:
        logging.error(f"Could not connect to MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Could not connect to the database.")

# Retrieve the database instance
async def get_db() -> Any:
    if database is None:
        logging.error("Database not initialized.")
        raise HTTPException(status_code=500, detail="Database not initialized.")
    return database

# Retrieve a collection asynchronously with validation
async def get_collection(collection_name: str) -> Any:
    db = await get_db()
    if not collection_name.isidentifier():  # Ensure collection name is valid
        raise HTTPException(status_code=400, detail="Invalid collection name.")
    return db[collection_name]

# CRUD Helpers

# Find one document in a collection
async def find_one(collection: str, query: dict) -> Optional[dict]:
    try:
        result = await (await get_collection(collection)).find_one(query)
        if result:
            result['_id'] = str(result['_id'])  # Convert ObjectId to string
        return result
    except PyMongoError as e:
        logging.error(f"Error finding document: {e}")
        raise HTTPException(status_code=500, detail="Error finding document.")

# Find multiple documents in a collection
async def find_many(collection: str, query: dict = {}, limit: int = 10) -> List[dict]:
    try:
        cursor = (await get_collection(collection)).find(query).limit(limit)
        results = []
        async for document in cursor:
            document['_id'] = str(document['_id'])  # Convert ObjectId to string
            results.append(document)
        return results
    except PyMongoError as e:
        logging.error(f"Error retrieving documents: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving documents.")

# Insert one document into a collection
async def insert_one(collection: str, data: dict) -> str:
    try:
        result = await (await get_collection(collection)).insert_one(data)
        return str(result.inserted_id)
    except PyMongoError as e:
        logging.error(f"Failed to insert document: {e}")
        raise HTTPException(status_code=500, detail="Could not insert document.")

# Update one document in a collection
async def update_one(collection: str, query: dict, update_data: dict) -> bool:
    try:
        result = await (await get_collection(collection)).update_one(query, {"$set": update_data})
        return result.modified_count > 0
    except PyMongoError as e:
        logging.error(f"Failed to update document: {e}")
        raise HTTPException(status_code=500, detail="Could not update document.")

# Delete one document from a collection
async def delete_one(collection: str, query: dict) -> bool:
    try:
        result = await (await get_collection(collection)).delete_one(query)
        return result.deleted_count > 0
    except PyMongoError as e:
        logging.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail="Could not delete document.")

# Validate ObjectId format
def is_valid_object_id(id_str: str) -> bool:
    try:
        ObjectId(id_str)
        return True
    except Exception:
        return False

# Get a document by its ID
async def get_by_id(collection: str, id: str) -> Any:
    if not is_valid_object_id(id):
        raise HTTPException(status_code=400, detail="Invalid ID format.")
    
    try:
        document = await find_one(collection, {"_id": ObjectId(id)})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")
        return document
    except PyMongoError as e:
        logging.error(f"Error retrieving document by ID: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving document by ID.")

# Close MongoDB connection
async def close_db():
    global client
    if client:
        client.close()
        logging.info("Closed MongoDB connection.")
